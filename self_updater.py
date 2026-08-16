"""Provjera, preuzimanje i sigurna instalacija izdanja s GitHuba."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


class SelfUpdater:
    """Preuzima samo službeni paket najnovijeg GitHub Releasea."""

    CHUNK_SIZE = 256 * 1024

    def __init__(self, root, version: str, repo: str, button_getter, language_getter) -> None:
        self.root = root
        self.version = version
        self.repo = repo
        self.button_getter = button_getter
        self.language_getter = language_getter
        self.running = False
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
            request = urllib.request.Request(
                f"https://api.github.com/repos/{self.repo}/releases/latest",
                headers={"Accept": "application/vnd.github+json", "User-Agent": f"Digitalni-sef/{self.version}"},
            )
            with urllib.request.urlopen(request, timeout=15) as response:
                release = json.loads(response.read().decode("utf-8"))
            if release.get("draft") or release.get("prerelease"):
                raise ValueError("Nema dostupnog stabilnog izdanja.")
            self.root.after(0, lambda: self._checked(release, manual))
        except (OSError, TimeoutError, ValueError, json.JSONDecodeError, urllib.error.URLError) as error:
            self.root.after(0, lambda: self._failed(str(error), manual))

    def _checked(self, release: dict, manual: bool) -> None:
        self.running = False
        self._set_button(True)
        latest = str(release.get("tag_name", "")).strip()
        release_url = str(release.get("html_url") or f"https://github.com/{self.repo}/releases/latest")
        if not latest:
            self._failed(self._text("GitHub nije vratio verziju izdanja."), manual)
            return
        if not self._is_newer(latest, self.version):
            if manual:
                messagebox.showinfo(self._text("Ažuriranje"), self._text("Koristite najnoviju verziju ({version}).").format(version=self.version), parent=self.root)
            return
        prompt = self._text("Dostupna je verzija {latest} (trenutno {current}).\n\nŽelite li je preuzeti i instalirati?").format(latest=latest, current=self.version)
        if not messagebox.askyesno(self._text("Dostupno ažuriranje"), prompt, parent=self.root):
            return
        asset = self._matching_asset(release.get("assets", []))
        if not getattr(sys, "frozen", False) or asset is None:
            messagebox.showinfo(
                self._text("Ažuriranje"),
                self._text("Automatska instalacija dostupna je za Windows EXE i Linux AppImage. Otvorena je stranica izdanja za ručno preuzimanje."),
                parent=self.root,
            )
            webbrowser.open(release_url, new=2)
            return
        self.running = True
        self._set_button(False)
        self._show_progress(latest)
        threading.Thread(target=self._download_worker, args=(asset,), daemon=True).start()

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
        title = tk.Label(frame, text=self._text("Ažuriranje na {version}").format(version=latest), font=("TkDefaultFont", 12, "bold"))
        title.pack(anchor="w")
        self.progress_label = tk.Label(frame, text=self._text("Preuzimanje ažuriranja..."))
        self.progress_label.pack(anchor="w", pady=(12, 6))

        row = tk.Frame(frame)
        row.pack(fill="x")
        self.progress_bar = ttk.Progressbar(row, orient="horizontal", mode="determinate", maximum=100, length=330)
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

    def _download_worker(self, asset: dict) -> None:
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

            with urllib.request.urlopen(request, timeout=90) as response, package.open("wb") as output:
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

            self.root.after(0, lambda: self._begin_install(package, staging))
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
                self.progress_bar.configure(mode="determinate", value=percent)
            if self.progress_percent:
                self.progress_percent.configure(text=f"{percent}%")
            detail = f"{self._mb(downloaded)} / {self._mb(total)}"
        else:
            if self.progress_bar:
                self.progress_bar.configure(mode="indeterminate")
                self.progress_bar.start(10)
            if self.progress_percent:
                self.progress_percent.configure(text="")
            detail = self._mb(downloaded)
        if self.progress_detail:
            self.progress_detail.configure(text=detail)

    def _begin_install(self, package: Path, staging: Path) -> None:
        if self.progress_bar:
            try:
                self.progress_bar.stop()
            except tk.TclError:
                pass
            self.progress_bar.configure(mode="determinate", value=100)
        if self.progress_percent:
            self.progress_percent.configure(text="100%")
        if self.progress_label:
            self.progress_label.configure(text=self._text("Instaliranje ažuriranja..."))
        if self.progress_detail:
            self.progress_detail.configure(text=self._text("Provjera je završena. Priprema instalacije."))
        threading.Thread(target=self._install_worker, args=(package, staging), daemon=True).start()

    def _install_worker(self, package: Path, staging: Path) -> None:
        try:
            if sys.platform.startswith("win"):
                self._start_windows_replace(package, staging)
                self.root.after(0, self._restart_ready)
                return
            if sys.platform.startswith("linux") and os.environ.get("APPIMAGE"):
                self._replace_linux_appimage(package, staging)
                self.root.after(0, self._restart_ready)
                return
            raise OSError(self._text("Automatska instalacija nije podržana za ovaj paket."))
        except OSError as error:
            shutil.rmtree(staging, ignore_errors=True)
            self.root.after(0, lambda: self._install_failed(str(error)))

    def _replace_linux_appimage(self, package: Path, staging: Path) -> None:
        executable = Path(os.environ["APPIMAGE"]).expanduser().resolve()
        parent = executable.parent
        if not executable.exists():
            raise OSError(self._text("Trenutni AppImage nije pronađen."))
        if not os.access(parent, os.W_OK) or not os.access(executable, os.W_OK):
            raise OSError(self._text("Nema dozvole za zamjenu trenutnog AppImagea. Premjestite ga u mapu u koju imate pravo pisanja."))

        replacement = parent / f".{executable.name}.update"
        shutil.copy2(package, replacement)
        os.chmod(replacement, 0o755)
        if replacement.stat().st_size != package.stat().st_size:
            replacement.unlink(missing_ok=True)
            raise OSError(self._text("Provjera instalacijske datoteke nije uspjela."))
        os.replace(replacement, executable)
        subprocess.Popen([str(executable)], cwd=str(parent), start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.rmtree(staging, ignore_errors=True)

    def _start_windows_replace(self, package: Path, staging: Path) -> None:
        script = staging / "install-update.bat"
        executable = Path(sys.executable).resolve()
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
            ]), encoding="utf-8",
        )
        subprocess.Popen(["cmd", "/c", str(script)], close_fds=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

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
        self.root.after(900, self.root.destroy)

    def _matching_asset(self, assets: object) -> dict | None:
        if not isinstance(assets, list):
            return None
        suffix = ".exe" if sys.platform.startswith("win") else ".AppImage" if sys.platform.startswith("linux") and os.environ.get("APPIMAGE") else ""
        if not suffix:
            return None
        candidates = [asset for asset in assets if isinstance(asset, dict) and str(asset.get("name", "")).endswith(suffix)]
        if not candidates:
            return None
        # Prefer x86_64/amd64 builds when several packages of the same type exist.
        return next((asset for asset in candidates if any(token in str(asset.get("name", "")).lower() for token in ("x86_64", "amd64"))), candidates[0])

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
        return croatian if self.language_getter() != "en" else {
            "Ažuriranje": "Update",
            "Provjera ažuriranja već je u tijeku.": "An update check is already running.",
            "GitHub nije vratio verziju izdanja.": "GitHub did not return a release version.",
            "Koristite najnoviju verziju ({version}).": "You are using the latest version ({version}).",
            "Dostupna je verzija {latest} (trenutno {current}).\n\nŽelite li je preuzeti i instalirati?": "Version {latest} is available (current: {current}).\n\nDo you want to download and install it?",
            "Dostupno ažuriranje": "Update available",
            "Ažuriranje na {version}": "Updating to {version}",
            "Preuzimanje ažuriranja...": "Downloading update...",
            "Instaliranje ažuriranja...": "Installing update...",
            "Provjera je završena. Priprema instalacije.": "Verification complete. Preparing installation.",
            "Ažuriranje je instalirano.": "Update installed.",
            "Ponovno pokretanje Digitalnog sefa...": "Restarting Digital Vault...",
            "Automatska instalacija dostupna je za Windows EXE i Linux AppImage. Otvorena je stranica izdanja za ručno preuzimanje.": "Automatic installation is available for Windows EXE and Linux AppImage. The release page has been opened for manual download.",
            "Preuzeta datoteka je prazna.": "The downloaded file is empty.",
            "Preuzimanje nije potpuno.": "The download is incomplete.",
            "Sigurnosna provjera preuzete datoteke nije uspjela.": "The downloaded file failed its security verification.",
            "Automatska instalacija nije podržana za ovaj paket.": "Automatic installation is not supported for this package.",
            "Trenutni AppImage nije pronađen.": "The current AppImage could not be found.",
            "Nema dozvole za zamjenu trenutnog AppImagea. Premjestite ga u mapu u koju imate pravo pisanja.": "The current AppImage cannot be replaced because the folder is not writable. Move it to a folder you can write to.",
            "Provjera instalacijske datoteke nije uspjela.": "The installation file verification failed.",
            "Ažuriranje nije uspjelo": "Update failed",
            "Provjera ažuriranja nije uspjela": "Update check failed",
            "Preuzimanje ažuriranja nije uspjelo": "Update download failed",
        }.get(croatian, croatian)

    @staticmethod
    def _safe_name(name: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "-", name) or "update.bin"

    @staticmethod
    def _mb(value: int) -> str:
        return f"{value / (1024 * 1024):.1f} MB"

    @staticmethod
    def _is_newer(latest: str, current: str) -> bool:
        def parts(value: str) -> tuple[int, ...]:
            return tuple(int(part) for part in re.findall(r"\d+", value)) or (0,)
        left, right = parts(latest), parts(current)
        return left + (0,) * max(0, len(right) - len(left)) > right + (0,) * max(0, len(left) - len(right))
