"""Télécommande web : piloter l'écran depuis un téléphone du réseau local.

Le démon sert une page (GET /) et l'API (POST /api, même JSON que le socket) sur le
port choisi, pour tout le réseau local. Chaque appel doit porter le jeton (en-tête
X-Jeton) : l'adresse à ouvrir sur le téléphone le contient après « # » (jamais
envoyé au serveur ni gardé dans ses journaux). HTTP simple : à réserver à un réseau
de confiance, et à désactiver quand on ne s'en sert pas.

~/.config/rog-flare2/telecommande.json : {"actif": false, "port": 8765, "jeton": "..."}
"""
from __future__ import annotations

import hmac
import json
import secrets
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from rog_flare2_core import CONFIG_DIR

CONFIG_FILE = CONFIG_DIR / "telecommande.json"
MAX_BODY = 64 * 1024


def load_config() -> dict:
    try:
        cfg = json.loads(CONFIG_FILE.read_text())
    except (OSError, ValueError):
        cfg = {}
    cfg = {"actif": False, "port": 8765, **cfg}
    if not cfg.get("jeton"):
        cfg["jeton"] = secrets.token_urlsafe(18)
        save_config(cfg)
    return cfg


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=1))
    CONFIG_FILE.chmod(0o600)


def new_token() -> str:
    cfg = load_config()
    cfg["jeton"] = secrets.token_urlsafe(18)
    save_config(cfg)
    return cfg["jeton"]


def lan_address() -> str:
    """Adresse de ce PC sur le réseau local (aucun paquet n'est envoyé)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("192.0.2.1", 9))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def url(cfg: dict | None = None) -> str:
    cfg = cfg or load_config()
    return f"http://{lan_address()}:{cfg['port']}/#{cfg['jeton']}"


def catalogue() -> dict:
    """Ce que la page propose : effets, favoris, listes, cadrans, positions des LED."""
    from rog_flare2_effets import AUDIO_EFFECTS, EFFECTS, effect_label
    from rog_flare2_listes import load_favorites, load_lists
    from rog_flare2_simulateur import _positions
    pos = _positions(1.0, 0.0)
    w, h = max(x for x, _y in pos), max(y for _x, y in pos)
    return {"effets": [[n, effect_label(n)] for n in [*EFFECTS, *AUDIO_EFFECTS]],
            "favoris": [[f.get("label", "?"), f.get("show")] for f in load_favorites()],
            "listes": sorted(load_lists()),
            "leds": [[round(x / w, 4), round(y / h, 4)] for x, y in pos], "ratio": round(h / w, 4)}


def page() -> bytes:
    from rog_flare2_i18n import _
    texts = {"clock": _("Horloge"), "gallery": _("Galerie GIF"), "stop": _("Arrêter"),
             "brightness": _("Luminosité"), "effect": _("▶ Lancer l'effet"), "favorites": _("Favoris"),
             "lists": _("Listes de lecture"), "notify": _("Afficher"), "message": _("Message à afficher"),
             "noToken": _("Jeton absent ou refusé : ouvrez l'adresse complète affichée dans le lanceur "
                          "(Réglages → Télécommande web)."),
             "playing": _("En cours :"), "nothing": _("Rien")}
    return PAGE.replace("__TEXTS__", json.dumps(texts, ensure_ascii=False)).encode()


class RemoteServer:
    """Serveur HTTP de la télécommande (fil du démon)."""

    def __init__(self, handle):
        self.handle = handle  # Daemon.handle
        self.httpd: ThreadingHTTPServer | None = None
        self.token = ""

    def start(self, cfg: dict) -> bool:
        self.stop()
        if not cfg.get("actif"):
            return False
        self.token = cfg["jeton"]
        server = self

        class H(BaseHTTPRequestHandler):
            def _send(self, code: int, body: bytes, kind: str):
                self.send_response(code)
                self.send_header("Content-Type", kind)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path.split("?")[0] in ("/", "/index.html"):
                    self._send(200, page(), "text/html; charset=utf-8")
                else:
                    self.send_error(404)

            def do_POST(self):
                if self.path != "/api":
                    self.send_error(404)
                    return
                if not hmac.compare_digest(self.headers.get("X-Jeton", ""), server.token):
                    self._send(403, b'{"ok": false, "error": "jeton"}', "application/json")
                    return
                size = int(self.headers.get("Content-Length", 0))
                if size > MAX_BODY:
                    self.send_error(413)
                    return
                try:
                    req = json.loads(self.rfile.read(size))
                    resp = server.handle(req)
                except Exception as exc:
                    resp = {"ok": False, "error": str(exc)}
                self._send(200, json.dumps(resp, ensure_ascii=False).encode(), "application/json")

            def log_message(self, *_a):
                pass

        try:
            self.httpd = ThreadingHTTPServer(("0.0.0.0", int(cfg.get("port", 8765))), H)
        except OSError as exc:
            print(f"télécommande : port {cfg.get('port')} indisponible ({exc})", flush=True)
            return False
        self.httpd.daemon_threads = True
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        return True

    def stop(self):
        if self.httpd is not None:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None


PAGE = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AniMe Matrix</title>
<style>
:root{--bg:#0e0f12;--card:#17191f;--fg:#eceef2;--muted:#8a8f99;--accent:#e0263a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.4 system-ui,sans-serif}
main{max-width:520px;margin:0 auto;padding:16px}
h1{font-size:1.3em;margin:4px 0 12px;color:var(--accent)}
.card{background:var(--card);border-radius:14px;padding:12px;margin-bottom:12px}
canvas{width:100%;display:block}
.row{display:flex;gap:8px;flex-wrap:wrap}.row>*{flex:1 1 auto}
button{background:#23262e;color:var(--fg);border:1px solid #2e323c;border-radius:10px;padding:12px;font:inherit;min-width:0}
button.main{background:var(--accent);border-color:var(--accent);color:#fff}
select,input[type=text]{width:100%;background:#0e0f12;color:var(--fg);border:1px solid #2e323c;border-radius:10px;padding:10px;font:inherit}
input[type=range]{width:100%;accent-color:var(--accent)}
.muted{color:var(--muted);font-size:.9em}h2{font-size:1em;margin:0 0 8px;color:var(--muted);font-weight:600}
#err{display:none;color:#ff8a95}
</style></head><body><main>
<h1>AniMe Matrix</h1>
<p id="err"></p>
<div class="card"><canvas id="screen"></canvas><p class="muted" id="now"></p></div>
<div class="card row"><button class="main" id="clock"></button><button id="gallery"></button><button id="stop"></button></div>
<div class="card"><h2 id="lb"></h2><input type="range" id="bright" min="0" max="100"></div>
<div class="card"><select id="effects"></select><div class="row" style="margin-top:8px"><button id="effect"></button></div></div>
<div class="card" id="favcard"><h2 id="lfav"></h2><div class="row" id="favs"></div></div>
<div class="card" id="listcard"><h2 id="llists"></h2><div class="row" id="lists"></div></div>
<div class="card"><input type="text" id="msg" maxlength="200"><div class="row" style="margin-top:8px"><button id="notify"></button></div></div>
</main><script>
const T=__TEXTS__;const token=location.hash.slice(1);let leds=[],ratio=1,names={};
const $=id=>document.getElementById(id);
async function api(body){const r=await fetch("/api",{method:"POST",headers:{"Content-Type":"application/json","X-Jeton":token},body:JSON.stringify(body)});
 if(r.status==403){$("err").textContent=T.noToken;$("err").style.display="block";throw new Error("jeton")}return r.json()}
function play(show){return api({cmd:"play",show})}
function btn(label,fn){const b=document.createElement("button");b.textContent=label;b.onclick=fn;return b}
function draw(b64){const c=$("screen"),w=c.clientWidth,h=Math.round(w*ratio*0.9)+16;c.width=w*devicePixelRatio;c.height=h*devicePixelRatio;
 const g=c.getContext("2d");g.scale(devicePixelRatio,devicePixelRatio);g.fillStyle="#0b0b0d";g.fillRect(0,0,w,h);
 const v=b64?Uint8Array.from(atob(b64),ch=>ch.charCodeAt(0)):[];const r=Math.max(1.5,w/19/2.6);
 leds.forEach((p,i)=>{const x=8+p[0]*(w-16),y=8+p[1]*(h-16),l=(v[i]||0)/255;
  g.fillStyle=l>0?`rgba(255,${Math.round(40+60*l)},${Math.round(40+60*l)},${0.25+0.75*l})`:"#1c1d22";g.beginPath();g.arc(x,y,r,0,7);g.fill()})}
function label(show){if(!show)return T.nothing;if(show.type=="effet")return names[show.name]||show.name;
 if(show.type=="horloge")return T.clock;if(show.type=="liste")return show.name;if(show.type=="gif")return T.gallery;return show.type}
async function poll(){try{const f=await api({cmd:"frame"});draw(f.frame);const s=await api({cmd:"status"});
 $("now").textContent=T.playing+" "+label(s.show);if(document.activeElement!==$("bright"))$("bright").value=s.brightness}catch(e){}
 setTimeout(poll,700)}
async function init(){for(const[k,id]of[["clock","clock"],["gallery","gallery"],["stop","stop"],["effect","effect"],["notify","notify"]])$(id).textContent=T[k];
 $("lb").textContent=T.brightness;$("lfav").textContent=T.favorites;$("llists").textContent=T.lists;$("msg").placeholder=T.message;
 const c=await api({cmd:"catalogue"});leds=c.leds;ratio=c.ratio;
 for(const[n,l]of c.effets){names[n]=l;const o=document.createElement("option");o.value=n;o.textContent=l;$("effects").append(o)}
 if(!c.favoris.length)$("favcard").style.display="none";for(const[l,s]of c.favoris)$("favs").append(btn(l,()=>play(s)));
 if(!c.listes.length)$("listcard").style.display="none";for(const n of c.listes)$("lists").append(btn(n,()=>play({type:"liste",name:n})));
 $("clock").onclick=()=>play({type:"horloge"});$("stop").onclick=()=>api({cmd:"stop"});
 $("gallery").onclick=()=>api({cmd:"galerie"});
 $("effect").onclick=()=>play({type:"effet",name:$("effects").value,params:{},speed:1});
 $("bright").oninput=e=>api({cmd:"brightness",value:+e.target.value});
 $("notify").onclick=()=>{const m=$("msg").value.trim();if(m)api({cmd:"notify",text:m,duration:0})};
 poll()}
init();
</script></body></html>
"""
