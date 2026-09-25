"""Client OpenRGB (SDK, protocole 0) contre un faux serveur : décodage, recherche, couleurs, synchronisation."""
import socketserver
import struct
import threading
import time

import pytest

import rog_flare2_openrgb as O


def s(text):
    b = text.encode() + b"\0"
    return struct.pack("<H", len(b)) + b


def controller(name, n_leds):
    mode = s("Direct") + struct.pack("<iIIIIIIII", 15, 32, 0, 0, 0, 0, 0, 0, 1) + struct.pack("<H", 0)
    mode2 = s("Static") + struct.pack("<iIIIIIIII", 0, 336, 0, 0, 1, 1, 0, 0, 2) + struct.pack("<H", 1) + b"\x10\x20\x30\x00"
    zone = s("Keyboard") + struct.pack("<iIII", 2, n_leds, n_leds, n_leds) + struct.pack("<H", 0)
    leds = b"".join(s(f"Key {i}") + struct.pack("<I", i) for i in range(n_leds))
    body = (struct.pack("<i", 5) + s(name) + s("desc") + s("1.0") + s("") + s("HID")
            + struct.pack("<H", 2) + struct.pack("<i", 0) + mode + mode2
            + struct.pack("<H", 1) + zone + struct.pack("<H", n_leds) + leds
            + struct.pack("<H", n_leds) + b"\x00\x00\x00\x00" * n_leds)
    return struct.pack("<I", 4 + len(body)) + body


DEVICES = [controller("ENE DRAM", 8), controller("ASUS ROG Strix Flare II Animate", 5)]


@pytest.fixture
def server():
    received = []

    class H(socketserver.BaseRequestHandler):
        def handle(self):
            while True:
                head = self.request.recv(16, 0x100)
                if len(head) < 16:
                    return
                _m, dev, pkt, size = struct.unpack("<4sIII", head)
                data = self.request.recv(size, 0x100) if size else b""
                received.append((dev, pkt, data))
                if pkt == O.REQUEST_CONTROLLER_COUNT:
                    reply = struct.pack("<I", len(DEVICES))
                elif pkt == O.REQUEST_CONTROLLER_DATA:
                    reply = DEVICES[dev]
                else:
                    continue
                self.request.sendall(b"ORGB" + struct.pack("<III", dev, pkt, len(reply)) + reply)

    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), H)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield srv.server_address[1], received
    srv.shutdown()
    srv.server_close()


def test_parse_and_find(server):
    port, _ = server
    c = O.OpenRGBClient(port=port)
    devs = c.controllers()
    assert [d["num_leds"] for d in devs] == [8, 5] and len(devs[1]["modes"]) == 2
    assert c.find()["index"] == 1
    c.close()


def test_set_all_packet(server):
    port, received = server
    c = O.OpenRGBClient(port=port)
    c.direct(1)
    c.set_all(1, 5, (224, 38, 58))
    c.close()
    time.sleep(0.2)
    pkt = [r for r in received if r[1] == O.UPDATELEDS][0]
    assert pkt[0] == 1 and struct.unpack_from("<IH", pkt[2]) == (4 + 2 + 20, 5) and pkt[2][6:9] == bytes((224, 38, 58))
    assert any(r[1] == O.SETCUSTOMMODE for r in received)


@pytest.mark.parametrize("mode,level,expected", [("theme", 0.0, (224, 38, 58)), ("pulsation", 1.0, (224, 38, 58)),
                                                 ("pulsation", 0.0, (33, 5, 8))])
def test_keyboard_sync(server, monkeypatch, mode, level, expected):
    port, received = server
    monkeypatch.setattr(O, "PORT", port)
    monkeypatch.setattr(O.OpenRGBClient.__init__, "__defaults__", ("127.0.0.1", port, 3))
    sync = O.KeyboardSync(lambda: level, lambda: "#e0263a")
    sync.start({"mode": mode, "serveur": False})
    time.sleep(0.6)
    sync.stop()
    leds = [r for r in received if r[1] == O.UPDATELEDS]
    assert leds and leds[-1][2][6:9] == bytes(expected) and sync.status == mode


def test_off_does_nothing():
    sync = O.KeyboardSync(lambda: 0, lambda: "#ffffff")
    sync.start({"mode": "off"})
    assert sync.thread is None and sync.status == "off"
