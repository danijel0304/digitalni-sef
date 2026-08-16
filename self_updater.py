"""Provjera, preuzimanje i instalacija novih izdanja s GitHuba."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


class SelfUpdater:
    """Updater za source, Windows EXE i Linux EXE/AppImage/DEB/RPM/TAR instalacije."""

    CHUNK_SIZE = 256 * 1024

    def __init__(self, root, version: str, repo: str, button_getter, language_getter) -> None:
        self.root = root
        self.version = version
        self.repo = repo
        self.button_getter = button_getter
        self.language_getter = language_getter
        self.running = False
        self.latest = ""
        self.progress_window: tk.Toplevel | None = None
        self.progress_bar: ttk.Progressbar | None = None
        self.progress_label: tk.Label | None = None
        self.progress_detail: tk.Label | None = None
        self.progress_percent: tk.Label | None = None

    def check(self, manual: bool = True) -> None:
        if self.running:
            if manual:
                messagebox.showinfo(self._text("Ažuriranje"), self._text("Provjera ažuriranja već je u tijeku."), parent=self.root)
            return
        self.running = True
        self._set_button(False)
        threading.Thread(target=self._check_worker, args=(manual,), daemon=True).start()

    def _check_worker(self, manual: bool) -> None:
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{self.repo}/releases/latest",
                headers={"Accept": "application/vnd.github+json", "User-Agent": f"Digitalni-sef/{self.version}"},
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                release = json.loads(response.read().decode("utf-8"))
            if release.get("draft") or release.get("prerelease"):
                raise ValueError(self._text("Nema dostupnog stabilnog izdanja."))
            self.root.after(0, lambda: self._checked(release, manual))
        except (OSError, TimeoutError, ValueError, json.JSONDecodeError, urllib.error.URLError) as error:
            self.root.after(0, lambda: self._failed(str(error), manual))

    def _checked(self, release: dict, manual: bool) -> None:
        self.running = False
        self._set_button(True)
        latest = str(release.get("tag_name", "")).strip()
        if not latest:
            self._failed(self._text("GitHub nije vratio verziju izdanja."), manual)
            return
        if not self._is_newer(latest, self.version):
            if manual:
                messagebox.showinfo(
                    self._text("Ažuriranje"),
                    self._text("Koristite najnoviju verziju ({version}).").format(version=self.version),
                    parent=self.root,
                )
            return

        prompt = self._text(
            "Dostupna je verzija {latest} (trenutno {current}).\n\nŽelite li je preuzeti i instalirati?"
        ).format(latest=latest, current=self.version)
        if not messagebox.askyesno(self._text("Dostupno ažuriranje"), prompt, parent=self.root):
            return

        self.latest = latest
        mode = self._install_mode()
        asset = None if mode == "source" else self._matching_asset(release.get("assets", []), mode)
        if mode != "source" and asset is None:
            messagebox.showwarning(
                self._text("Ažuriranje"),
                self._text("Za ovu instalaciju nije pronađen odgovarajući paket. Otvara se stranica izdanja."),
                parent=self.root,
            )
            webbrowser.open(str(release.get("html_url") or f"https://github.com/{self.repo}/releases/latest"), new=2)
            return

        if mode == "source":
            asset = {
                "name": f"digitalni-sef-{latest}-source.tar.gz",
                "browser_download_url": str(release.get("tarball_url") or f"https://api.github.com/repos/{self.repo}/tarball/{latest}"),
                "size": 0,
                "digest": "",
            }

        self.running = True
        self._set_button(False)
        self._show_progress(latest)
        threading.Thread(target=self._download_worker, args=(asset, mode), daemon=True).start()

    def _show_progress(self, latest: str) -> None:
        self._close_progress()
        window = tk.Toplevel(self.root)
        self.progress_window = window
        window.title(self._text("Ažuriranje"))
        window.resizable(False, False)
        window.transient(self.root)
        window.protocol("WM_DELETE_WINDOW", lambda: None)

        frame = tk.Frame(window, padx=24, pady=20)
        frame.pack(fill="both", expand=True)
        tk.Label(
            frame,
            text=self._text("Ažuriranje na {version}").format(version=latest),
            font=("TkDefaultFont", 12, "bold"),
        ).pack(anchor="w")
        self.progress_label = tk.Label(frame, text=self._text("Preuzimanje ažuriranja..."))
        self.progress_label.pack(anchor="w", pady=(12, 6))

        row = tk.Frame(frame)
        row.pack(fill="x")
        self.progress_bar = ttk.Progressbar(row, orient="horizontal", mode="determinate", maximum=100, length=340)
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.progress_percent = tk.Label(row, text="0%", width=5, anchor="e")
        self.progress_percent.pack(side="left", padx=(10, 0))
        self.progress_detail = tk.Label(frame, text="0 MB", anchor="w")
        self.progress_detail.pack(fill="x", pady=(6, 0))

        window.update_idletasks()
        try:
            x = self.root.winfo_rootx() + max(0, (self.root.winfo_width() - window.winfo_width()) // 2)
            y = self.root.winfo_rooty() + max(0, (self.root.winfo_height() - window.winfo_height()) // 2)
            window.geometry(f"+{x}+{y}")
        except tk.TclError:
            pass
        window.grab_set()

    def _download_worker(self, asset: dict, mode: str) -> None:
        staging: Path | None = None
        try:
            url = str(asset["browser_download_url"])
            name = self._safe_name(str(asset["name"]))
            staging = Path(tempfile.mkdtemp(prefix="digitalni-sef-update-"))
            package = staging / name
            request = urllib.request.Request(url, headers={"User-Agent": f"Digitalni-sef/{self.version}"})
            sha256 = hashlib.sha256()
            downloaded = 0
            expected = int(asset.get("size") or 0)

            with urllib.request.urlopen(request, timeout=120) as response, package.open("wb") as output:
                header_total = response.headers.get("Content-Length")
                if header_total and str(header_total).isdigit():
                    expected = int(header_total)
                while True:
                    chunk = response.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    output.write(chunk)
                    sha256.update(chunk)
                    downloaded += len(chunk)
                    self.root.after(0, lambda done=downloaded, total=expected: self._update_download_progress(done, total))

            if downloaded <= 0:
                raise ValueError(self._text("Preuzeta datoteka je prazna."))
            if expected and downloaded != expected:
                raise ValueError(self._text("Preuzimanje nije potpuno."))

            digest = str(asset.get("digest") or "")
            if digest.lower().startswith("sha256:"):
                expected_digest = digest.split(":", 1)[1].strip().lower()
                if expected_digest and sha256.hexdigest().lower() != expected_digest:
                    raise ValueError(self._text("Sigurnosna provjera preuzete datoteke nije uspjela."))

            self.root.after(0, lambda: self._begin_install(package, staging, mode))
        except (OSError, KeyError, ValueError, urllib.error.URLError) as error:
            if staging:
                shutil.rmtree(staging, ignore_errors=True)
            self.root.after(0, lambda: self._download_failed(str(error)))

    def _update_download_progress(self, downloaded: int, total: int) -> None:
        if not self.progress_window or not self.progress_window.winfo_exists():
            return
        if total > 0:
            percent = min(100, int(downloaded * 100 / total))
            if self.progress_bar:
                self.progress_bar.stop()
                self.progress_bar.configure(mode="determinate", value=percent)
            if self.progress_percent:
                self.progress_percent.configure(text=f"{percent}%")
            detail = f"{self._mb(downloaded)} / {self._mb(total)}"
        else:
            if self.progress_bar:
                self.progress_bar.configure(mode="indeterminate")
                self.progress_bar.start(12)
            if self.progress_percent:
                self.progress_percent.configure(text="")
            detail = self._mb(downloaded)
        if self.progress_detail:
            self.progress_detail.configure(text=detail)

    def _begin_install(self, package: Path, staging: Path, mode: str) -> None:
        if self.progress_bar:
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate", value=100)
        if self.progress_percent:
            self.progress_percent.configure(text="100%")
        if self.progress_label:
            self.progress_label.configure(text=self._text("Instaliranje ažuriranja..."))
        if self.progress_detail:
            self.progress_detail.configure(text=self._text("Preuzimanje i provjera su završeni."))
        threading.Thread(target=self._install_worker, args=(package, staging, mode), daemon=True).start()

    def _install_worker(self, package: Path, staging: Path, mode: str) -> None:
        try:
            if mode == "source":
                self._install_source(package, staging)
                self.root.after(0, self._restart_ready)
                return
            if mode == "windows-exe":
                self._start_windows_replace(package, staging)
                self.root.after(0, self._restart_ready)
                return
            if mode == "appimage":
                self._start_appimage_replace(package, staging)
                self.root.after(0, self._restart_ready)
                return
            if mode in ("deb", "rpm"):
                self._start_system_package_install(package, staging, mode)
                self.root.after(0, self._restart_ready)
                return
            if mode == "tar":
                self._start_tar_replace(package, staging)
                self.root.after(0, self._restart_ready)
                return
            raise OSError(self._text("Automatska instalacija nije podržana za ovaj paket."))
        except (OSError, tarfile.TarError) as error:
            shutil.rmtree(staging, ignore_errors=True)
            self.root.after(0, lambda: self._install_failed(str(error)))

    def _install_source(self, package: Path, staging: Path) -> None:
        project = Path(__file__).resolve().parent
        extracted = staging / "source"
        extracted.mkdir(parents=True, exist_ok=True)
        with tarfile.open(package, "r:gz") as archive:
            self._safe_extract(archive, extracted)
        roots = [p for p in extracted.iterdir() if p.is_dir()]
        source = roots[0] if len(roots) == 1 else extracted

        skip = {".git", "__pycache__", ".venv", "venv", ".idea"}
        for item in source.iterdir():
            if item.name in skip:
                continue
            target = project / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)

        launcher = project / "pokreni.sh"
        if launcher.exists():
            os.chmod(launcher, launcher.stat().st_mode | 0o111)
        version_file = project / "digitalni_sef_version.txt"
        version_file.write_text(self.latest + "\n", encoding="utf-8")
        shutil.rmtree(staging, ignore_errors=True)

        if sys.platform.startswith("win"):
            launcher_bat = project / "pokreni.bat"
            if launcher_bat.exists():
                subprocess.Popen(["cmd", "/c", str(launcher_bat)], cwd=str(project), start_new_session=True)
            else:
                subprocess.Popen([sys.executable, str(project / "app.py")], cwd=str(project), start_new_session=True)
        else:
            subprocess.Popen(["bash", str(launcher)], cwd=str(project), start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _start_windows_replace(self, package: Path, staging: Path) -> None:
        executable = Path(sys.executable).resolve()
        script = staging / "install-update.bat"
        script.write_text(
            "\r\n".join([
                "@echo off",
                "setlocal",
                "timeout /t 2 /nobreak >nul",
                f'copy /Y "{package}" "{executable}" >nul',
                "if errorlevel 1 exit /b 1",
                f'start "" "{executable}"',
                f'rmdir /S /Q "{staging}"',
                'del "%~f0"',
            ]),
            encoding="utf-8",
        )
        subprocess.Popen(["cmd", "/c", str(script)], close_fds=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

    def _start_appimage_replace(self, package: Path, staging: Path) -> None:
        executable = Path(os.environ["APPIMAGE"]).expanduser().resolve()
        if not executable.exists():
            raise OSError(self._text("Trenutni AppImage nije pronađen."))
        if not os.access(executable.parent, os.W_OK):
            raise OSError(self._text("Nema dozvole za zamjenu trenutnog AppImagea."))

        script = staging / "install-update.sh"
        script.write_text(
            "\n".join([
                "#!/bin/sh",
                "sleep 2",
                f'cp -f "{package}" "{executable}" || exit 1',
                f'chmod +x "{executable}"',
                f'"{executable}" >/dev/null 2>&1 &',
                f'rm -rf "{staging}"',
            ]),
            encoding="utf-8",
        )
        os.chmod(script, 0o700)
        subprocess.Popen(["sh", str(script)], start_new_session=True)

    def _start_system_package_install(self, package: Path, staging: Path, mode: str) -> None:
        if shutil.which("pkexec") is None:
            raise OSError(self._text("Za automatsku instalaciju DEB/RPM paketa potreban je pkexec."))
        executable = Path(sys.executable).resolve()
        command = ["dpkg", "-i", str(package)] if mode == "deb" else ["rpm", "-U", "--replacepkgs", str(package)]
        script = staging / "install-system-package.sh"
        quoted = " ".join(self._shell_quote(part) for part in command)
        script.write_text(
            "\n".join([
                "#!/bin/sh",
                "sleep 2",
                f'pkexec {quoted} || exit 1',
                f'"{executable}" >/dev/null 2>&1 &',
                f'rm -rf "{staging}"',
            ]),
            encoding="utf-8",
        )
        os.chmod(script, 0o700)
        subprocess.Popen(["sh", str(script)], start_new_session=True)

    def _start_tar_replace(self, package: Path, staging: Path) -> None:
        executable = Path(sys.executable).resolve()
        current_dir = executable.parent
        if current_dir.name != "Digitalni-sef":
            raise OSError(self._text("Nije prepoznata TAR instalacija Digitalnog sefa."))

        extracted = staging / "tar"
        extracted.mkdir(parents=True, exist_ok=True)
        with tarfile.open(package, "r:gz") as archive:
            self._safe_extract(archive, extracted)
        new_dir = extracted / "Digitalni-sef"
        new_exe = new_dir / executable.name
        if not new_exe.exists():
            raise OSError(self._text("Novi TAR paket nema očekivanu izvršnu datoteku."))

        parent = current_dir.parent
        if not os.access(parent, os.W_OK):
            raise OSError(self._text("Nema dozvole za zamjenu TAR instalacije."))

        script = staging / "install-tar-update.sh"
        script.write_text(
            "\n".join([
                "#!/bin/sh",
                "sleep 2",
                f'rm -rf "{current_dir}.old"',
                f'mv "{current_dir}" "{current_dir}.old" || exit 1',
                f'mv "{new_dir}" "{current_dir}" || {{ mv "{current_dir}.old" "{current_dir}"; exit 1; }}',
                f'rm -rf "{current_dir}.old"',
                f'"{current_dir / executable.name}" >/dev/null 2>&1 &',
                f'rm -rf "{staging}"',
            ]),
            encoding="utf-8",
        )
        os.chmod(script, 0o700)
        subprocess.Popen(["sh", str(script)], start_new_session=True)

    def _restart_ready(self) -> None:
        self.running = False
        if self.progress_label:
            self.progress_label.configure(text=self._text("Ažuriranje je instalirano."))
        if self.progress_detail:
            self.progress_detail.configure(text=self._text("Ponovno pokretanje Digitalnog sefa..."))
        if self.progress_percent:
            self.progress_percent.configure(text="100%")
        if self.progress_bar:
            self.progress_bar.configure(value=100)
        self.root.after(1000, self.root.destroy)

    def _install_mode(self) -> str:
        if not getattr(sys, "frozen", False):
            return "source"
        if sys.platform.startswith("win"):
            return "windows-exe"
        if sys.platform.startswith("linux"):
            if os.environ.get("APPIMAGE"):
                return "appimage"
            executable = Path(sys.executable).resolve()
            if str(executable).startswith("/usr/lib/digitalni-sef/"):
                return self._linux_package_family()
            if executable.parent.name == "Digitalni-sef":
                return "tar"
            return self._linux_package_family()
        return "unsupported"

    def _linux_package_family(self) -> str:
        data = {}
        try:
            for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    data[key] = value.strip().strip('"').lower()
        except OSError:
            pass
        family = " ".join([data.get("ID", ""), data.get("ID_LIKE", "")])
        if any(token in family for token in ("fedora", "rhel", "centos", "suse", "opensuse")):
            return "rpm"
        if any(token in family for token in ("debian", "ubuntu", "mint", "pop")):
            return "deb"
        return "tar"

    def _matching_asset(self, assets: object, mode: str) -> dict | None:
        if not isinstance(assets, list):
            return None
        suffixes = {
            "windows-exe": (".exe",),
            "appimage": (".AppImage",),
            "deb": (".deb",),
            "rpm": (".rpm",),
            "tar": (".tar.gz",),
        }.get(mode, ())
        candidates = [
            asset for asset in assets
            if isinstance(asset, dict) and any(str(asset.get("name", "")).endswith(suffix) for suffix in suffixes)
        ]
        if not candidates:
            return None
        return next(
            (a for a in candidates if any(t in str(a.get("name", "")).lower() for t in ("x86_64", "amd64"))),
            candidates[0],
        )

    def _failed(self, error: str, manual: bool) -> None:
        self.running = False
        self._set_button(True)
        if manual:
            messagebox.showwarning(self._text("Provjera ažuriranja nije uspjela"), error, parent=self.root)

    def _download_failed(self, error: str) -> None:
        self.running = False
        self._set_button(True)
        self._close_progress()
        messagebox.showerror(self._text("Preuzimanje ažuriranja nije uspjelo"), error, parent=self.root)

    def _install_failed(self, error: str) -> None:
        self.running = False
        self._set_button(True)
        self._close_progress()
        messagebox.showerror(self._text("Ažuriranje nije uspjelo"), error, parent=self.root)

    def _close_progress(self) -> None:
        if self.progress_window:
            try:
                if self.progress_window.winfo_exists():
                    try:
                        self.progress_window.grab_release()
                    except tk.TclError:
                        pass
                    self.progress_window.destroy()
            except tk.TclError:
                pass
        self.progress_window = None
        self.progress_bar = None
        self.progress_label = None
        self.progress_detail = None
        self.progress_percent = None

    def _set_button(self, enabled: bool) -> None:
        button = self.button_getter()
        if button:
            button.configure(state="normal" if enabled else "disabled")

    def _text(self, croatian: str) -> str:
        if self.language_getter() != "en":
            return croatian
        return {
            "Ažuriranje": "Update",
            "Provjera ažuriranja već je u tijeku.": "An update check is already running.",
            "Nema dostupnog stabilnog izdanja.": "No stable release is available.",
            "GitHub nije vratio verziju izdanja.": "GitHub did not return a release version.",
            "Koristite najnoviju verziju ({version}).": "You are using the latest version ({version}).",
            "Dostupna je verzija {latest} (trenutno {current}).\n\nŽelite li je preuzeti i instalirati?": "Version {latest} is available (current: {current}).\n\nDo you want to download and install it?",
            "Dostupno ažuriranje": "Update available",
            "Ažuriranje na {version}": "Updating to {version}",
            "Preuzimanje ažuriranja...": "Downloading update...",
            "Instaliranje ažuriranja...": "Installing update...",
            "Preuzimanje i provjera su završeni.": "Download and verification complete.",
            "Ažuriranje je instalirano.": "Update installed.",
            "Ponovno pokretanje Digitalnog sefa...": "Restarting Digital Vault...",
            "Provjera ažuriranja nije uspjela": "Update check failed",
            "Preuzimanje ažuriranja nije uspjelo": "Update download failed",
            "Ažuriranje nije uspjelo": "Update failed",
            "Preuzeta datoteka je prazna.": "The downloaded file is empty.",
            "Preuzimanje nije potpuno.": "The download is incomplete.",
            "Sigurnosna provjera preuzete datoteke nije uspjela.": "Downloaded file verification failed.",
            "Za ovu instalaciju nije pronađen odgovarajući paket. Otvara se stranica izdanja.": "No matching package was found for this installation. Opening the release page.",
            "Automatska instalacija nije podržana za ovaj paket.": "Automatic installation is not supported for this package.",
            "Trenutni AppImage nije pronađen.": "The current AppImage was not found.",
            "Nema dozvole za zamjenu trenutnog AppImagea.": "No permission to replace the current AppImage.",
            "Za automatsku instalaciju DEB/RPM paketa potreban je pkexec.": "pkexec is required for automatic DEB/RPM installation.",
            "Nije prepoznata TAR instalacija Digitalnog sefa.": "Digital Vault TAR installation was not recognized.",
            "Novi TAR paket nema očekivanu izvršnu datoteku.": "The new TAR package does not contain the expected executable.",
            "Nema dozvole za zamjenu TAR instalacije.": "No permission to replace the TAR installation.",
        }.get(croatian, croatian)

    @staticmethod
    def _safe_extract(archive: tarfile.TarFile, destination: Path) -> None:
        destination = destination.resolve()
        for member in archive.getmembers():
            target = (destination / member.name).resolve()
            if destination != target and destination not in target.parents:
                raise tarfile.TarError("Unsafe path in update archive.")
        archive.extractall(destination)

    @staticmethod
    def _safe_name(name: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "-", name) or "update.bin"

    @staticmethod
    def _shell_quote(value: str) -> str:
        return "'" + value.replace("'", "'\"'\"'") + "'"

    @staticmethod
    def _mb(value: int) -> str:
        return f"{value / (1024 * 1024):.1f} MB"

    @staticmethod
    def _is_newer(latest: str, current: str) -> bool:
        def parts(value: str) -> tuple[int, ...]:
            return tuple(int(part) for part in re.findall(r"\d+", value)) or (0,)
        left, right = parts(latest), parts(current)
        width = max(len(left), len(right))
        return left + (0,) * (width - len(left)) > right + (0,) * (width - len(right))
