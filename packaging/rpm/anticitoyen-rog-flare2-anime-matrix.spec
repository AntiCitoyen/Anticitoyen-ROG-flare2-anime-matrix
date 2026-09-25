Name:           anticitoyen-rog-flare2-anime-matrix
Version:        @VERSION@
Release:        1%{?dist}
Summary:        AniMe Matrix display tools for the ASUS ROG Strix Flare II Animate
License:        MIT
URL:            https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix
Source0:        %{url}/archive/v%{version}/Anticitoyen-ROG-flare2-anime-matrix-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  python3
Requires:       python3 >= 3.10, python3-hidapi, python3-pillow, python3-pillow-tk, python3-numpy, python3-tkinter
Recommends:     python3-xlib, python3-gobject, libayatana-appindicator-gtk3, ImageMagick, pulseaudio-utils
Recommends:     zenity, python3-pynput, libnotify, xdg-user-dirs

%description
Linux tools for the 312-LED AniMe Matrix display of the ASUS ROG Strix Flare II
Animate keyboard (USB 0b05:19fc): launcher with round layouts, GIF gallery,
clock, effects and audio visualizers, games, system monitor, desktop
notifications, schedule, animation editor, community library, OpenRGB sync.

%prep
%autosetup -n Anticitoyen-ROG-flare2-anime-matrix-%{version}

%build

%install
packaging/install.sh %{buildroot} %{_prefix} %{__python3}

%files
%license LICENSE
%{_bindir}/animematrix*
%{_datadir}/%{name}/
%{_prefix}/lib/systemd/user/animematrixd.service
%{_prefix}/lib/udev/rules.d/72-rog-flare2-animate.rules
%{_datadir}/applications/animematrix.desktop
%{_datadir}/icons/hicolor/scalable/apps/animematrix.svg
%doc %{_datadir}/doc/%{name}/

%post
udevadm control --reload-rules >/dev/null 2>&1 || :
systemctl --global enable animematrixd.service >/dev/null 2>&1 || :

%preun
if [ $1 -eq 0 ]; then systemctl --global disable animematrixd.service >/dev/null 2>&1 || :; fi

%changelog
* Fri Sep 25 2026 AntiCitoyen <anticitoyen@users.noreply.gitlab.com> - @VERSION@-1
- See https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases
