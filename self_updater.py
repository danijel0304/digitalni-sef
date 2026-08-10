"""Provjera i sigurna zamjena izdanja preuzetih s GitHuba."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from tkinter import messagebox


class SelfUpdater:
    """Preuzima samo službeni paket najnovijeg GitHub Releasea."""

    def __init__(self, root, version: str, repo: str, button_getter, language_getter) -> None:
        self.root = root
        self.version = version
        self.repo = repo
        self.button_getter = button_getter
        self.language_getter = language_getter
        self.running = False

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
            with urllib.request.urlopen(request, timeout=10) as response:
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
            webbrowser.open(release_url, new=2)
            return
        self.running = True
        self._set_button(False)
        threading.Thread(target=self._download_worker, args=(asset,), daemon=True).start()

    def _download_worker(self, asset: dict) -> None:
        try:
            url = str(asset["browser_download_url"])
            name = self._safe_name(str(asset["name"]))
            staging = Path(tempfile.mkdtemp(prefix="digitalni-sef-update-"))
            package = staging / name
            request = urllib.request.Request(url, headers={"User-Agent": f"Digitalni-sef/{self.version}"})
            with urllib.request.urlopen(request, timeout=90) as response, package.open("wb") as output:
                shutil.copyfileobj(response, output)
            self.root.after(0, lambda: self._install(package, staging))
        except (OSError, KeyError, ValueError, urllib.error.URLError) as error:
            self.root.after(0, lambda: self._download_failed(str(error)))

    def _install(self, package: Path, staging: Path) -> None:
        self.running = False
        self._set_button(True)
        try:
            if sys.platform.startswith("win"):
                self._start_windows_replace(package, staging)
            elif sys.platform.startswith("linux") and os.environ.get("APPIMAGE"):
                self._start_linux_replace(package, staging)
            else:
                webbrowser.open(f"https://github.com/{self.repo}/releases/latest", new=2)
                return
        except OSError as error:
            messagebox.showerror(self._text("Ažuriranje nije uspjelo"), str(error), parent=self.root)
            return
        messagebox.showinfo(self._text("Ažuriranje"), self._text("Ažuriranje je preuzeto. Digitalni sef će se ponovno pokrenuti."), parent=self.root)
        self.root.after(400, self.root.destroy)

    def _start_windows_replace(self, package: Path, staging: Path) -> None:
        script = staging / "install-update.bat"
        executable = Path(sys.executable).resolve()
        script.write_text(
            "\r\n".join([
                "@echo off", "timeout /t 2 /nobreak >nul",
                f'copy /Y "{package}" "{executable}" >nul',
                f'start "" "{executable}"', f'rmdir /S /Q "{staging}"', 'del "%~f0"',
            ]), encoding="utf-8",
        )
        subprocess.Popen(["cmd", "/c", str(script)], close_fds=True)

    def _start_linux_replace(self, package: Path, staging: Path) -> None:
        script = staging / "install-update.sh"
        executable = Path(os.environ["APPIMAGE"]).resolve()
        script.write_text(
            "\n".join([
                "#!/bin/sh", "sleep 2",
                f'cp -f "{package}" "{executable}"', f'chmod +x "{executable}"', f'"{executable}" >/dev/null 2>&1 &',
                f'rm -rf "{staging}"',
            ]), encoding="utf-8",
        )
        os.chmod(script, 0o700)
        subprocess.Popen(["sh", str(script)], close_fds=True)

    def _matching_asset(self, assets: object) -> dict | None:
        if not isinstance(assets, list):
            return None
        suffix = ".exe" if sys.platform.startswith("win") else ".AppImage" if sys.platform.startswith("linux") and os.environ.get("APPIMAGE") else ""
        if not suffix:
            return None
        return next((asset for asset in assets if isinstance(asset, dict) and str(asset.get("name", "")).endswith(suffix)), None)

    def _failed(self, error: str, manual: bool) -> None:
        self.running = False
        self._set_button(True)
        if manual:
            messagebox.showwarning(self._text("Provjera ažuriranja nije uspjela"), error, parent=self.root)

    def _download_failed(self, error: str) -> None:
        self.running = False
        self._set_button(True)
        messagebox.showerror(self._text("Preuzimanje ažuriranja nije uspjelo"), error, parent=self.root)

    def _set_button(self, enabled: bool) -> None:
        button = self.button_getter()
        if button:
            button.configure(state="normal" if enabled else "disabled")

    def _text(self, croatian: str) -> str:
        return croatian if self.language_getter() != "en" else {
            "Ažuriranje": "Update", "Provjera ažuriranja već je u tijeku.": "An update check is already running.",
            "GitHub nije vratio verziju izdanja.": "GitHub did not return a release version.",
            "Koristite najnoviju verziju ({version}).": "You are using the latest version ({version}).",
            "Dostupna je verzija {latest} (trenutno {current}).\n\nŽelite li je preuzeti i instalirati?": "Version {latest} is available (current: {current}).\n\nDo you want to download and install it?",
            "Dostupno ažuriranje": "Update available", "Ažuriranje nije uspjelo": "Update failed",
            "Ažuriranje je preuzeto. Digitalni sef će se ponovno pokrenuti.": "The update was downloaded. Digital Vault will restart.",
            "Provjera ažuriranja nije uspjela": "Update check failed", "Preuzimanje ažuriranja nije uspjelo": "Update download failed",
        }.get(croatian, croatian)

    @staticmethod
    def _safe_name(name: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "-", name) or "update.zip"

    @staticmethod
    def _is_newer(latest: str, current: str) -> bool:
        def parts(value: str) -> tuple[int, ...]:
            return tuple(int(part) for part in re.findall(r"\d+", value)) or (0,)
        left, right = parts(latest), parts(current)
        return left + (0,) * max(0, len(right) - len(left)) > right + (0,) * max(0, len(left) - len(right))
