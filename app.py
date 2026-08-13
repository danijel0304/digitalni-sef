"""Digitalni sef – lokalna evidencija računa i pretplata.

Pokreni: python3 app.py
"""
from __future__ import annotations

import base64
import calendar
import json
import os
import secrets
import sys
import tempfile
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import END, PhotoImage, StringVar, TclError, filedialog, messagebox

import customtkinter as ctk
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image

from service_catalog import SERVICE_CATALOG
from self_updater import SelfUpdater


APP_DIR = Path.home() / ".digitalni_sef"
LEGACY_APP_DIR = Path.home() / ".servisni_sef"
CONFIG_FILE = APP_DIR / "config.json"
VAULT_FILE = APP_DIR / "vault.json"
CATEGORY_CATALOG_FILE = APP_DIR / "catalog.json"
ATTACHMENTS_DIR = APP_DIR / "attachments"
ICON_FILES = {
    "dark": Path(__file__).resolve().parent / "assets" / "digitalni-sef-dark.png",
    "light": Path(__file__).resolve().parent / "assets" / "digitalni-sef-light.png",
}
PAYPAL_DONATION_URL = "https://www.paypal.com/paypalme/danijel0304"
GITHUB_REPO = "danijel0304/digitalni-sef"
VAULT_CHECK = b"digitalni-sef-check"
LEGACY_VAULT_CHECK = b"servisni-sef-check"
BACKUP_VERSION = 1
CURRENT_LANGUAGE = "en"
CATALOG_PAGE_SIZE = 50


def app_version() -> str:
    resource_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    for path in (resource_dir / "digitalni_sef_version.txt", Path(__file__).resolve().parent / "digitalni_sef_version.txt"):
        try:
            version = path.read_text(encoding="utf-8").strip()
            if version:
                return version
        except OSError:
            pass
    return "v1.0.3"


APP_VERSION = app_version()

ENGLISH = {
    "Digitalni sef": "Digital Vault", "Vaši digitalni računi na jednom mjestu": "Your digital accounts in one place",
    "Vaši računi, pretplate i jamstva na sigurnom.": "Your accounts, subscriptions, and warranties kept safe.",
    "Vaši računi, pretplate i jamstva.": "Your accounts, subscriptions, and warranties.",
    "Moje usluge": "My services", "Dodaj uslugu": "Add service", "Nova usluga": "New service", "Uredi uslugu": "Edit service",
    "Uredi podatke": "Edit details", "Spremi promjene": "Save changes", "Zatvori": "Close", "Uredi zapis": "Edit record", "Obriši": "Delete",
    "Pregled usluga": "Service overview", "Sigurno i lokalno": "Secure and local", "Lokalno šifrirano": "Encrypted locally",
    "Lozinke se ne šalju nikamo.": "Passwords are never sent anywhere.", "Svijetla tema": "Light theme", "Tamna tema": "Dark theme",
    "Hrvatski": "Croatian", "Jezik": "Language", "Doniraj putem PayPala": "Donate via PayPal",
    "Pretplate, računi i jamstva prodavatelja na jednom sigurnom mjestu.": "Subscriptions, accounts, and seller warranties in one secure place.",
    "Pretraži usluge, prodavatelja ili kategoriju...": "Search services, sellers, or categories...", "Sve": "All", "Sve kategorije": "All categories",
    "Sve usluge": "All services", "Istječe uskoro": "Expiring soon", "Isteklo": "Expired", "Automatska obnova": "Auto-renewal",
    "UKUPNO USLUGA": "TOTAL SERVICES", "MJ. TROŠAK": "MONTHLY COST", "ISTJEČE U 30 DANA": "EXPIRES IN 30 DAYS",
    "Nema roka": "No deadline", "Lozinka nije spremljena": "No password saved", "Nema dodatnih podataka": "No additional details",
    "Kupnja": "Purchase", "Chat": "Chat", "E-mail": "Email", "Lozinka": "Password", "Korisničko ime": "Username",
    "Detalji spremljene usluge": "Saved service details", "Kategorija": "Category", "Prodavatelj": "Seller", "Kupljeno": "Purchased",
    "Korisničko ime prodavatelja": "Seller username", "Pretplata vrijedi do": "Subscription valid until", "Jamstvo vrijedi do": "Warranty valid until",
    "Trošak": "Cost", "Bilješke": "Notes", "Nema bilješki.": "No notes.", "Privici": "Attachments", "Privitak": "Attachment",
    "Otvori kupnju": "Open purchase", "Otvori chat s prodavateljem": "Open seller chat", "Privitak nije moguće otvoriti": "Unable to open attachment",
    "Trošak i obnova": "Cost & renewal", "Podaci služe za pregled troškova i podsjetnike.": "Used for cost summaries and reminders.",
    "Cijena po naplati": "Price per charge", "Valuta": "Currency", "Učestalost naplate": "Billing frequency", "Mjesečno": "Monthly",
    "Godišnje": "Yearly", "Jednokratno": "One-time", "Da": "Yes", "Ne": "No", "Sljedeća naplata": "Next charge",
    "Podsjetnik": "Reminder", "Bez podsjetnika": "No reminder", "dana prije": "days before", "Podsjetnik dana prije": "Reminder days before", "Spremi postavke": "Save settings",
    "Dodaj račun / PDF": "Add receipt / PDF", "Privici ({count})": "Attachments ({count})", "Postavi datum": "Set date", "Jamstvo": "Warranty",
    "Trajanje od kupnje": "Duration from purchase", "mjesec(i)": "month(s)", "godina(e)": "year(s)", "dana": "days",
    "Naziv usluge * — pišite za prijedloge": "Service name * — type for suggestions", "Polja označena zvjezdicom su obavezna.": "Fields marked with an asterisk are required.",
    "E-mail / korisničko ime": "Email / username", "Kupljeno (DD.MM.GGGG.)": "Purchased (DD.MM.YYYY)",
    "Jamstvo prodavatelja vrijedi do": "Seller warranty valid until", "Prodavatelj / gdje je kupljeno": "Seller / where purchased",
    "Poveznica na kupnju": "Purchase link", "Poveznica na chat s prodavateljem": "Seller chat link",
    "Podsjetnici": "Reminders", "Rokovi koje ste označili za podsjetnik.": "Dates you marked for a reminder.",
    "Nema nadolazećih podsjetnika.": "No upcoming reminders.", "Pretplata istječe": "Subscription expires", "Jamstvo istječe": "Warranty expires",
    "Sigurnosna kopija": "Backup", "Vrati kopiju": "Restore backup", "Spremi šifriranu sigurnosnu kopiju": "Save encrypted backup",
    "Odaberite sigurnosnu kopiju": "Choose a backup", "Sigurnosna kopija spremljena": "Backup saved", "Kopija vraćena": "Backup restored",
    "Kopija je šifrirana vašom glavnom lozinkom.": "The backup is encrypted with your master password.",
    "Zapisi i šifrirani privici su vraćeni.": "Records and encrypted attachments were restored.",
    "Glavna lozinka": "Master password", "Ponovite glavnu lozinku": "Repeat master password", "Otključaj sef": "Unlock vault",
    "Izradi sigurni sef": "Create secure vault", "Zaboravili ste glavnu lozinku?": "Forgot your master password?",
    "Postavite glavnu lozinku za vaš novi sef.": "Set the master password for your new vault.",
    "Unesite glavnu lozinku za otključavanje sefa.": "Enter your master password to unlock the vault.",
    "Glavna lozinka se ne može vratiti. Čuvajte je na sigurnom.": "The master password cannot be recovered. Keep it safe.",
    "Provjeri ažuriranja": "Check for updates",
    "Cjelokupno trajanje pretplate": "Entire subscription term", "Naplata": "Charge", "Istječe": "Expires",
    "Isteklo prije {days} d.": "Expired {days} days ago", "{action} danas": "{action} today", "{action} za {days} d.": "{action} in {days} days", "{action}: {date}": "{action}: {date}",
}


def tr(value: str) -> str:
    """Translate interface text while leaving user-entered data untouched."""
    return ENGLISH.get(value, value) if CURRENT_LANGUAGE == "en" else value


def original_text(value: str) -> str:
    if CURRENT_LANGUAGE != "en":
        return value
    return next((croatian for croatian, english in ENGLISH.items() if english == value), value)


def _localize_widget(widget_type, keys: tuple[str, ...]) -> None:
    original_init = widget_type.__init__

    def localized_init(self, *args, **kwargs):
        for key in keys:
            if isinstance(kwargs.get(key), str):
                kwargs[key] = tr(kwargs[key])
        original_init(self, *args, **kwargs)

    widget_type.__init__ = localized_init


_localize_widget(ctk.CTkLabel, ("text",))
_localize_widget(ctk.CTkButton, ("text",))
_localize_widget(ctk.CTkEntry, ("placeholder_text",))

DARK_COLORS = {
    "bg": "#0B1020", "panel": "#121A2D", "panel_hover": "#19243D",
    "input": "#0E1627", "accent": "#6D5DFB", "accent_hover": "#5C4EDE",
    "text": "#F5F7FF", "muted": "#94A3B8", "border": "#273551",
    "success": "#2DD4A8", "warning": "#FBBF24", "danger": "#FB7185",
    "sidebar": "#0D1526", "sidebar_card": "#17233C", "badge": "#202C44",
}
LIGHT_COLORS = {
    "bg": "#F4F7FC", "panel": "#FFFFFF", "panel_hover": "#EAF0FA",
    "input": "#F8FAFD", "accent": "#6254E8", "accent_hover": "#5145CC",
    "text": "#172033", "muted": "#637087", "border": "#D7E0EE",
    "success": "#079669", "warning": "#BC7800", "danger": "#D53B58",
    "sidebar": "#FFFFFF", "sidebar_card": "#EDF1FF", "badge": "#EEF2F8",
}
COLORS = DARK_COLORS.copy()

ENGLISH.update({
    "Pregled": "Overview", "Katalog usluga": "Service catalog", "Troškovi": "Costs",
    "Brzo dodavanje": "Quick add", "Istražite usluge": "Explore services",
    "Odaberite uslugu i otvorit ćemo obrazac s već popunjenim nazivom i kategorijom.": "Choose a service and we will open a form with its name and category already filled in.",
    "Sve vrste": "All types", "Pronađeno usluga": "services found", "Dodaj": "Add",
    "Pregled potrošnje": "Spending overview", "Procijenjeni trošak na temelju unesenih pretplata.": "Estimated cost based on your saved subscriptions.",
    "MJESEČNO": "MONTHLY", "GODIŠNJE": "YEARLY", "JEDNOKRATNE KUPOVINE": "ONE-TIME PURCHASES",
    "Potrošnja po kategoriji": "Spending by category", "Nema unesenih cijena za prikaz.": "There are no saved prices to display.",
    "Najviše kategorija": "Top categories", "Aktivne pretplate": "Active subscriptions",
})


def parse_date(value: str) -> date | None:
    """Reads older ISO dates and the Croatian date format used in the interface."""
    if not value.strip():
        return None
    for date_format in ("%d.%m.%Y.", "%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.strip(), date_format).date()
        except ValueError:
            continue
    return None


def date_text(value: str) -> str:
    parsed = parse_date(value)
    return parsed.strftime("%d.%m.%Y.") if parsed else "—"


def date_value(value: date) -> str:
    return value.strftime("%d.%m.%Y.")


def add_months(start: date, months: int) -> date:
    """Adds calendar months without overflowing shorter months (e.g. 31 Jan -> 28 Feb)."""
    index = start.month - 1 + months
    year, month = start.year + index // 12, index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def parse_price(value: str) -> float | None:
    """Accept Croatian decimal commas while keeping stored values predictable."""
    if not value.strip():
        return None
    try:
        normalized = value.strip().replace(" ", "")
        if "," in normalized:
            normalized = normalized.replace(".", "").replace(",", ".")
        amount = float(normalized)
        return amount if amount >= 0 else None
    except ValueError:
        return None


def format_money(amount: float, currency: str) -> str:
    symbols = {"EUR": "€", "USD": "$", "GBP": "£"}
    return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" {symbols.get(currency, currency)}"


def monthly_amount(record: dict) -> float | None:
    amount = parse_price(str(record.get("price", "")))
    if amount is None or record.get("billing_cycle", "") == "Jednokratno":
        return None
    return amount / 12 if record.get("billing_cycle") == "Godišnje" else amount


class Vault:
    def __init__(self) -> None:
        # Existing users keep their data: the old hidden folder is renamed once.
        if not APP_DIR.exists() and LEGACY_APP_DIR.is_dir():
            try:
                LEGACY_APP_DIR.rename(APP_DIR)
            except OSError:
                pass
        APP_DIR.mkdir(exist_ok=True)
        self.fernet: Fernet | None = None

    @property
    def initialized(self) -> bool:
        return CONFIG_FILE.exists()

    @staticmethod
    def _key(master_password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480_000)
        return base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))

    def create(self, master_password: str) -> None:
        salt = os.urandom(16)
        key = self._key(master_password, salt)
        self.fernet = Fernet(key)
        CONFIG_FILE.write_text(json.dumps({
            "salt": base64.b64encode(salt).decode(),
            "check": self.fernet.encrypt(VAULT_CHECK).decode(),
        }), encoding="utf-8")
        if not VAULT_FILE.exists():
            VAULT_FILE.write_text("[]", encoding="utf-8")

    def unlock(self, master_password: str) -> bool:
        try:
            config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            key = self._key(master_password, base64.b64decode(config["salt"]))
            fernet = Fernet(key)
            if fernet.decrypt(config["check"]) not in (VAULT_CHECK, LEGACY_VAULT_CHECK):
                return False
            self.fernet = fernet
            return True
        except (OSError, KeyError, ValueError, InvalidToken):
            return False

    def theme(self) -> str:
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8")).get("theme", "dark")
        except (OSError, json.JSONDecodeError):
            return "dark"

    def save_theme(self, theme: str) -> None:
        try:
            config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            config["theme"] = theme
            CONFIG_FILE.write_text(json.dumps(config), encoding="utf-8")
        except (OSError, json.JSONDecodeError):
            pass

    def language(self) -> str:
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8")).get("language", "en")
        except (OSError, json.JSONDecodeError):
            return "en"

    def save_language(self, language: str) -> None:
        try:
            config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            config["language"] = language if language in ("hr", "en") else "hr"
            CONFIG_FILE.write_text(json.dumps(config), encoding="utf-8")
        except (OSError, json.JSONDecodeError):
            pass

    def load(self) -> list[dict]:
        try:
            return json.loads(VAULT_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

    def save(self, records: list[dict]) -> None:
        VAULT_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_catalog(self) -> dict[str, str]:
        """Combine built-in suggestions with the user's locally saved edits."""
        catalog = SERVICE_CATALOG.copy()
        try:
            changes = json.loads(CATEGORY_CATALOG_FILE.read_text(encoding="utf-8"))
            for name in changes.get("hidden", []):
                catalog.pop(str(name), None)
            catalog.update({str(name): str(category) for name, category in changes.get("custom", {}).items()})
        except (OSError, ValueError, TypeError):
            pass
        return catalog

    def save_catalog(self, catalog: dict[str, str]) -> None:
        """Save only changes so built-in catalog updates remain available."""
        custom = {name: category for name, category in catalog.items() if SERVICE_CATALOG.get(name) != category}
        hidden = sorted(name for name in SERVICE_CATALOG if name not in catalog)
        CATEGORY_CATALOG_FILE.write_text(json.dumps({"custom": custom, "hidden": hidden}, ensure_ascii=False, indent=2), encoding="utf-8")

    def export_backup(self, target: str, records: list[dict]) -> None:
        if not self.fernet:
            raise ValueError("Sef nije otključan.")
        attachments = {}
        for record in records:
            for attachment in record.get("attachments", []):
                stored_name = attachment.get("stored_name", "")
                source = ATTACHMENTS_DIR / stored_name
                if stored_name and source.is_file():
                    attachments[stored_name] = base64.b64encode(source.read_bytes()).decode("ascii")
        content = {"records": records, "attachments": attachments}
        encrypted = self.fernet.encrypt(json.dumps(content, ensure_ascii=False).encode("utf-8")).decode("utf-8")
        Path(target).write_text(json.dumps({
            "version": BACKUP_VERSION,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "data": encrypted,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    def import_backup(self, source: str) -> tuple[list[dict], dict[str, str]]:
        if not self.fernet:
            raise ValueError("Sef nije otključan.")
        payload = json.loads(Path(source).read_text(encoding="utf-8"))
        content = json.loads(self.fernet.decrypt(payload["data"].encode("utf-8")).decode("utf-8"))
        records = content.get("records", content) if isinstance(content, dict) else content
        attachments = content.get("attachments", {}) if isinstance(content, dict) else {}
        if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
            raise ValueError("Sigurnosna kopija nema ispravan sadržaj.")
        if not isinstance(attachments, dict) or not all(isinstance(name, str) and isinstance(data, str) for name, data in attachments.items()):
            raise ValueError("Sigurnosna kopija ima neispravne privitke.")
        return records, attachments

    def restore_attachments(self, attachments: dict[str, str]) -> None:
        if not attachments:
            return
        ATTACHMENTS_DIR.mkdir(exist_ok=True)
        for stored_name, data in attachments.items():
            if Path(stored_name).name != stored_name:
                raise ValueError("Neispravan naziv privitka u kopiji.")
            (ATTACHMENTS_DIR / stored_name).write_bytes(base64.b64decode(data))

    def save_attachment(self, source: str, record_id: str) -> dict:
        if not self.fernet:
            raise ValueError("Sef nije otključan.")
        source_path = Path(source)
        if not source_path.is_file():
            raise OSError("Datoteka više nije dostupna.")
        ATTACHMENTS_DIR.mkdir(exist_ok=True)
        attachment_id = secrets.token_hex(8)
        stored_name = f"{record_id}-{attachment_id}.bin"
        (ATTACHMENTS_DIR / stored_name).write_bytes(self.fernet.encrypt(source_path.read_bytes()))
        return {"id": attachment_id, "name": source_path.name, "stored_name": stored_name}

    def open_attachment(self, attachment: dict) -> None:
        if not self.fernet:
            raise ValueError("Sef nije otključan.")
        encrypted_file = ATTACHMENTS_DIR / attachment.get("stored_name", "")
        if not encrypted_file.is_file():
            raise OSError("Privitak nije pronađen.")
        suffix = Path(attachment.get("name", "")).suffix
        with tempfile.NamedTemporaryFile(prefix="digitalni-sef-", suffix=suffix, delete=False) as temporary:
            temporary.write(self.fernet.decrypt(encrypted_file.read_bytes()))
            temporary_path = Path(temporary.name)
        webbrowser.open(temporary_path.as_uri())

    def emergency_reset(self) -> None:
        """Remove only this vault when its master password can no longer be recovered."""
        CONFIG_FILE.unlink(missing_ok=True)
        VAULT_FILE.unlink(missing_ok=True)
        self.fernet = None

    def encrypt(self, password: str) -> str:
        return self.fernet.encrypt(password.encode()).decode() if password else ""

    def decrypt(self, token: str) -> str:
        if not token:
            return ""
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except (InvalidToken, AttributeError):
            return "[nije moguće dešifrirati]"


class LoginWindow(ctk.CTkToplevel):
    def __init__(self, app: "DigitalVault") -> None:
        super().__init__(app)
        self.app = app
        new_vault = not app.vault.initialized
        self.title(tr("Digitalni sef"))
        if app.app_icon:
            self.iconphoto(True, app.app_icon)
        self.geometry("480x455" if new_vault else "480x430")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.protocol("WM_DELETE_WINDOW", app.destroy)

        card = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=20)
        card.pack(expand=True, fill="both", padx=26, pady=26)
        ctk.CTkLabel(card, text="◈", font=("Arial", 36, "bold"), text_color=COLORS["accent"]).pack(pady=(35, 5))
        ctk.CTkLabel(card, text="Digitalni sef", font=("Arial", 25, "bold"), text_color=COLORS["text"]).pack()
        subtitle = "Postavite glavnu lozinku za vaš novi sef." if new_vault else "Unesite glavnu lozinku za otključavanje sefa."
        ctk.CTkLabel(card, text=subtitle, font=("Arial", 13), text_color=COLORS["muted"]).pack(pady=(7, 24))

        self.password = self.input(card, "Glavna lozinka", show="●")
        self.confirm = None
        if new_vault:
            self.confirm = self.input(card, "Ponovite glavnu lozinku", show="●")
        action = "Izradi sigurni sef" if new_vault else "Otključaj sef"
        ctk.CTkButton(card, text=action, height=43, corner_radius=10, fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], command=self.submit).pack(fill="x", padx=38, pady=(22, 6))
        if new_vault:
            ctk.CTkLabel(card, text="Glavna lozinka se ne može vratiti. Čuvajte je na sigurnom.", font=("Arial", 11), text_color=COLORS["muted"]).pack(pady=(6, 0))
        else:
            ctk.CTkButton(card, text="Zaboravili ste glavnu lozinku?", command=self.forgot_password,
                          height=30, fg_color="transparent", hover_color=COLORS["panel_hover"], text_color=COLORS["accent"], font=("Arial", 11, "underline")).pack(pady=(5, 0))
        self.wait_visibility()
        self.grab_set()
        self.after(150, self.password.focus_set)

    def input(self, parent, placeholder, show=None):
        field = ctk.CTkEntry(parent, placeholder_text=placeholder, show=show or "", height=43,
                             corner_radius=10, fg_color=COLORS["input"], border_color=COLORS["border"], text_color=COLORS["text"])
        field.pack(fill="x", padx=38, pady=6)
        field.bind("<Return>", lambda _event: self.submit())
        return field

    def submit(self) -> None:
        password = self.password.get()
        if len(password) < 8:
            messagebox.showwarning("Prekratka lozinka", "Glavna lozinka mora imati najmanje 8 znakova.", parent=self)
            return
        if not self.app.vault.initialized:
            if password != self.confirm.get():
                messagebox.showerror("Lozinke nisu jednake", "Unesite istu glavnu lozinku u oba polja.", parent=self)
                return
            self.show_master_password_notice(password)
            return
        elif not self.app.vault.unlock(password):
            messagebox.showerror("Nije moguće otključati", "Glavna lozinka nije točna.", parent=self)
            self.password.delete(0, END)
            return
        self.destroy()
        self.app.start()

    def show_master_password_notice(self, password: str) -> None:
        notice = ctk.CTkToplevel(self)
        notice.title("Važna sigurnosna obavijest")
        if self.app.app_icon:
            notice.iconphoto(True, self.app.app_icon)
        notice.geometry("535x385")
        notice.resizable(False, False)
        notice.configure(fg_color=COLORS["bg"])
        notice.transient(self)

        card = ctk.CTkFrame(notice, fg_color=COLORS["panel"], corner_radius=18)
        card.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(card, text="⚠", font=("Arial", 35, "bold"), text_color=COLORS["warning"]).pack(pady=(24, 4))
        ctk.CTkLabel(card, text="Ne zaboravite glavnu lozinku", font=("Arial", 21, "bold"), text_color=COLORS["text"]).pack()
        notice_text = (
            "Glavna lozinka štiti vaše spremljene lozinke i nije spremljena niti se može poslati e-poštom. "
            "Ako je zaboravite, postojeći šifrirani podaci neće se moći otvoriti. Tada ćete morati izraditi novi, prazan sef."
        )
        ctk.CTkLabel(card, text=notice_text, wraplength=425, justify="center", font=("Arial", 13), text_color=COLORS["muted"]).pack(padx=30, pady=(12, 16))
        ctk.CTkLabel(card, text="Spremite je na sigurno mjesto prije nastavka.", font=("Arial", 12, "bold"), text_color=COLORS["accent"]).pack(pady=(0, 12))
        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", padx=28, pady=(0, 20))
        ctk.CTkButton(buttons, text="Odustani", command=notice.destroy, height=40, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"]).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(buttons, text="Razumijem, izradi sef", command=lambda: self.finish_new_vault(notice, password), height=40, fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=("Arial", 12, "bold")).pack(side="left", expand=True, fill="x", padx=(6, 0))
        notice.wait_visibility()
        notice.grab_set()

    def finish_new_vault(self, notice: ctk.CTkToplevel, password: str) -> None:
        notice.destroy()
        self.app.vault.create(password)
        self.destroy()
        self.app.start()

    def forgot_password(self) -> None:
        messagebox.showinfo(
            "Sigurnosni postupak",
            "Glavna lozinka se ne šalje e-poštom i nije spremljena u aplikaciji — zato je nitko ne može ukrasti ili vratiti. "
            "Možete izraditi novi prazan sef s novom glavnom lozinkom. Time će svi postojeći zapisi ovog sefa biti trajno obrisani.",
            parent=self,
        )
        if not messagebox.askyesno("Novi sef", "Želite li nastaviti s brisanjem postojećeg sefa?", icon="warning", parent=self):
            return
        if not messagebox.askyesno("Potvrdite brisanje", "Ova se radnja briše sve spremljene usluge i lozinke. Nastaviti?", icon="warning", parent=self):
            return
        self.app.vault.emergency_reset()
        self.destroy()
        LoginWindow(self.app)


class SplashScreen(ctk.CTkToplevel):
    """Kratki uvodni ekran koji aplikaciji daje uglađeniji početak."""
    def __init__(self, app: "DigitalVault") -> None:
        super().__init__(app)
        self.app = app
        self.title(tr("Digitalni sef"))
        self.geometry("410x330")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.overrideredirect(True)
        self.protocol("WM_DELETE_WINDOW", app.destroy)
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 410) // 2
        y = (self.winfo_screenheight() - 330) // 2
        self.geometry(f"410x330+{x}+{y}")

        card = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=24)
        card.pack(expand=True, fill="both", padx=8, pady=8)
        icon_file = ICON_FILES[app.theme]
        if icon_file.exists():
            source = Image.open(icon_file)
            self.logo = ctk.CTkImage(light_image=source, dark_image=source, size=(118, 118))
            ctk.CTkLabel(card, text="", image=self.logo).pack(pady=(49, 12))
        ctk.CTkLabel(card, text="Digitalni sef", font=("Arial", 24, "bold"), text_color=COLORS["text"]).pack()
        ctk.CTkLabel(card, text="Vaši računi, pretplate i jamstva na sigurnom.", font=("Arial", 12), text_color=COLORS["muted"]).pack(pady=(5, 0))
        self.after(2000, self.finish)

    def finish(self) -> None:
        self.destroy()
        LoginWindow(self.app)


class CalendarPopup(ctk.CTkToplevel):
    """A small local calendar used for choosing ISO dates without extra packages."""
    def __init__(self, dialog: "RecordDialog", target: ctk.CTkEntry) -> None:
        super().__init__(dialog)
        self.target = target
        self.dialog = dialog
        self.current = parse_date(target.get()) or date.today()
        self.title(tr("Odaberite datum"))
        if dialog.app.app_icon:
            self.iconphoto(True, dialog.app.app_icon)
        self.geometry("320x350")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.transient(dialog)
        self.draw()
        self.wait_visibility()
        self.grab_set()

    def draw(self) -> None:
        for child in self.winfo_children():
            child.destroy()
        card = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=14)
        card.pack(expand=True, fill="both", padx=10, pady=10)
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkButton(header, text="‹", width=34, height=30, command=lambda: self.shift(-1), fg_color=COLORS["panel_hover"], hover_color=COLORS["border"]).pack(side="left")
        ctk.CTkLabel(header, text=f"{calendar.month_name[self.current.month]} {self.current.year}", font=("Arial", 14, "bold"), text_color=COLORS["text"]).pack(side="left", expand=True)
        ctk.CTkButton(header, text="›", width=34, height=30, command=lambda: self.shift(1), fg_color=COLORS["panel_hover"], hover_color=COLORS["border"]).pack(side="right")
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        for column, label in enumerate(("Po", "Ut", "Sr", "Če", "Pe", "Su", "Ne")):
            ctk.CTkLabel(grid, text=label, font=("Arial", 10, "bold"), text_color=COLORS["muted"]).grid(row=0, column=column, padx=2, pady=(2, 4), sticky="nsew")
            grid.grid_columnconfigure(column, weight=1)
        for row, week in enumerate(calendar.monthcalendar(self.current.year, self.current.month), start=1):
            for column, day_number in enumerate(week):
                if not day_number:
                    ctk.CTkLabel(grid, text="").grid(row=row, column=column, padx=2, pady=2, sticky="nsew")
                    continue
                chosen = date(self.current.year, self.current.month, day_number)
                highlighted = chosen == date.today()
                ctk.CTkButton(grid, text=str(day_number), height=28, width=30, corner_radius=7,
                              fg_color=COLORS["accent"] if highlighted else COLORS["panel_hover"],
                              hover_color=COLORS["accent_hover"] if highlighted else COLORS["border"],
                              text_color=COLORS["text"], font=("Arial", 11), command=lambda value=chosen: self.choose(value)).grid(row=row, column=column, padx=2, pady=2, sticky="nsew")

    def shift(self, amount: int) -> None:
        self.current = add_months(self.current.replace(day=1), amount)
        self.draw()

    def choose(self, value: date) -> None:
        self.dialog.set_date(self.target, value)
        self.destroy()


class WarrantyDurationDialog(ctk.CTkToplevel):
    def __init__(self, dialog: "RecordDialog") -> None:
        super().__init__(dialog)
        self.dialog = dialog
        self.title(tr("Trajanje jamstva"))
        if dialog.app.app_icon:
            self.iconphoto(True, dialog.app.app_icon)
        self.geometry("430x290")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.transient(dialog)
        card = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=16)
        card.pack(expand=True, fill="both", padx=18, pady=18)
        ctk.CTkLabel(card, text="Postavi jamstvo prodavatelja", font=("Arial", 18, "bold"), text_color=COLORS["text"]).pack(pady=(20, 5))
        ctk.CTkLabel(card, text="Trajanje se računa od datuma kupnje.", font=("Arial", 11), text_color=COLORS["muted"]).pack(pady=(0, 14))
        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.pack(fill="x", padx=30)
        self.amount = ctk.CTkEntry(controls, width=60, height=34, justify="center", placeholder_text="1", fg_color=COLORS["input"], border_color=COLORS["border"], text_color=COLORS["text"])
        self.amount.insert(0, "1")
        self.amount.pack(side="left", padx=(0, 6))
        self.unit = ctk.CTkOptionMenu(controls, values=[tr(value) for value in ("dana", "mjesec(i)", "godina(e)", "Cjelokupno trajanje pretplate")], command=self.update_amount_state, width=220, height=34, fg_color=COLORS["input"], button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"], text_color=COLORS["text"])
        self.unit.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(card, text="Postavi jamstvo", command=self.apply, height=39, corner_radius=9, fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=("Arial", 12, "bold")).pack(fill="x", padx=30, pady=(20, 5))
        self.wait_visibility()
        self.grab_set()

    def update_amount_state(self, unit: str) -> None:
        self.amount.configure(state="disabled" if unit == tr("Cjelokupno trajanje pretplate") else "normal")

    def apply(self) -> None:
        if self.dialog.calculate_warranty(self.amount.get(), self.unit.get()):
            self.destroy()


class SubscriptionOptionsDialog(ctk.CTkToplevel):
    """Keeps extra subscription settings accessible without crowding the main form."""
    def __init__(self, dialog: "RecordDialog") -> None:
        super().__init__(dialog)
        self.dialog = dialog
        self.title(tr("Trošak i obnova"))
        if dialog.app.app_icon:
            self.iconphoto(True, dialog.app.app_icon)
        self.geometry("500x490")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])

        card = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=16)
        card.pack(expand=True, fill="both", padx=18, pady=18)
        ctk.CTkLabel(card, text="Trošak i obnova", font=("Arial", 20, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=24, pady=(22, 2))
        ctk.CTkLabel(card, text="Podaci služe za pregled troškova i podsjetnike.", font=("Arial", 11), text_color=COLORS["muted"]).pack(anchor="w", padx=24, pady=(0, 14))

        values = dialog.subscription_values
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=3)
        self.price = self.add_entry(row, "Cijena po naplati", "npr. 9,99", values.get("price", ""), "left")
        self.currency = self.add_option(row, "Valuta", ["EUR", "USD", "GBP"], values.get("currency", "EUR"), "right")
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=3)
        self.cycle = self.add_option(row, "Učestalost naplate", ["Mjesečno", "Godišnje", "Jednokratno"], values.get("billing_cycle", "Mjesečno"), "left")
        self.auto_renew = self.add_option(row, "Automatska obnova", ["Ne", "Da"], values.get("auto_renew", "Ne"), "right")
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=3)
        self.renewal_date = self.add_date(row, "Sljedeća naplata", values.get("renewal_date", ""), "left")
        self.reminder_days = self.add_option(row, "Podsjetnik", ["Bez podsjetnika", "3", "7", "14", "30"], values.get("reminder_days", "7"), "right", suffix=" dana prije")
        ctk.CTkButton(card, text="Spremi postavke", command=self.apply, height=40, corner_radius=9,
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=("Arial", 12, "bold")).pack(fill="x", padx=24, pady=(22, 6))
        self.wait_visibility()
        self.grab_set()

    def field(self, parent, label: str, side: str):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side=side, expand=True, fill="x", padx=(0, 6) if side == "left" else (6, 0))
        ctk.CTkLabel(frame, text=label, font=("Arial", 10, "bold"), text_color=COLORS["muted"]).pack(anchor="w", pady=(0, 2))
        return frame

    def add_entry(self, parent, label: str, placeholder: str, value: str, side: str):
        field = ctk.CTkEntry(self.field(parent, label, side), placeholder_text=placeholder, height=34, corner_radius=9,
                             fg_color=COLORS["input"], border_color=COLORS["border"], text_color=COLORS["text"])
        field.pack(fill="x")
        field.insert(0, value)
        return field

    def add_option(self, parent, label: str, choices: list[str], value: str, side: str, suffix: str = ""):
        translated_choices = [tr(choice) for choice in choices]
        field = ctk.CTkOptionMenu(self.field(parent, label + suffix), values=translated_choices, height=34, corner_radius=9,
                                  fg_color=COLORS["input"], button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"], text_color=COLORS["text"])
        field.pack(fill="x")
        field.set(tr(value) if value in choices else translated_choices[0])
        return field

    def add_date(self, parent, label: str, value: str, side: str):
        field = ctk.CTkButton(self.field(parent, label, side), text="DD.MM.GGGG.", anchor="w", height=34, corner_radius=9,
                              border_width=1, fg_color=COLORS["input"], hover_color=COLORS["panel_hover"], border_color=COLORS["border"], text_color=COLORS["muted"], font=("Arial", 12))
        field.is_date_input, field.date_value = True, ""
        field.get = lambda control=field: control.date_value
        field.configure(command=lambda target=field: CalendarPopup(self.dialog, target))
        field.pack(fill="x")
        if parse_date(value):
            self.dialog.set_date(field, parse_date(value))
        return field

    def apply(self) -> None:
        price = self.price.get().strip()
        if price and parse_price(price) is None:
            messagebox.showwarning("Neispravna cijena", "Cijenu upišite kao npr. 9,99.", parent=self)
            return
        renewal = self.renewal_date.get().strip()
        if renewal and not parse_date(renewal):
            messagebox.showwarning("Neispravan datum", "Odaberite datum sljedeće naplate u kalendaru.", parent=self)
            return
        self.dialog.subscription_values = {
            "price": price, "currency": self.currency.get(), "billing_cycle": original_text(self.cycle.get()),
            "auto_renew": original_text(self.auto_renew.get()), "renewal_date": renewal, "reminder_days": original_text(self.reminder_days.get()),
        }
        self.dialog.update_subscription_button()
        self.destroy()


class RecordDialog(ctk.CTkToplevel):
    def __init__(self, app: "DigitalVault", record: dict | None = None, preset: dict | None = None) -> None:
        super().__init__(app)
        self.app, self.record, self.preset = app, record, preset or {}
        self.title(tr("Uredi uslugu") if record else tr("Dodaj uslugu"))
        if app.app_icon:
            self.iconphoto(True, app.app_icon)
        self.geometry("720x745")
        self.minsize(650, 710)
        self.configure(fg_color=COLORS["bg"])
        self.fields: dict[str, ctk.CTkEntry] = {}
        self.subscription_values = {
            "price": "", "currency": "EUR", "billing_cycle": "Mjesečno",
            "auto_renew": "Ne", "renewal_date": "", "reminder_days": "7",
        }
        if record:
            self.subscription_values.update({key: str(record.get(key, value)) for key, value in self.subscription_values.items()})
        self.attachments = list(record.get("attachments", [])) if record else []
        self.pending_attachments: list[str] = []

        # Obični okvir umjesto pomičnog dijela: pouzdan je na svim kombinacijama
        # CustomTkintera i Linux desktopa te se obrazac uvijek nacrta odmah.
        outer = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        outer.pack(expand=True, fill="both", padx=20, pady=16)
        ctk.CTkLabel(outer, text="Uredi podatke" if record else "Nova usluga", font=("Arial", 21, "bold"), text_color=COLORS["text"]).pack(anchor="w", pady=(1, 1))
        ctk.CTkLabel(outer, text="Polja označena zvjezdicom su obavezna.", text_color=COLORS["muted"], font=("Arial", 11)).pack(anchor="w", pady=(0, 7))

        ctk.CTkLabel(outer, text="Naziv usluge * — pišite za prijedloge", text_color=COLORS["muted"], font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))
        self.name_entry = ctk.CTkEntry(outer, placeholder_text="npr. Netflix, ChatGPT, EON...", height=34, corner_radius=9,
                                       fg_color=COLORS["input"], border_color=COLORS["border"], text_color=COLORS["text"])
        self.name_entry.pack(fill="x")
        self.fields["name"] = self.name_entry
        self.name_entry.bind("<KeyRelease>", self.filter_service_suggestions, add="+")
        self.suggestions = ctk.CTkFrame(outer, fg_color="transparent", height=31)
        self.suggestions.pack(fill="x", pady=(2, 3))
        self.show_hint("Počnite pisati za prijedloge ili upišite vlastitu uslugu.")
        row = ctk.CTkFrame(outer, fg_color="transparent")
        row.pack(fill="x", pady=1)
        self.add_field(row, "login", "E-mail / korisničko ime", "ime@primjer.hr", side="left")
        self.add_field(row, "password", "Lozinka", "Ostavite prazno ako je ne mijenjate", secret=True, side="right")
        row = ctk.CTkFrame(outer, fg_color="transparent")
        row.pack(fill="x", pady=1)
        self.add_field(row, "purchase_date", "Kupljeno (DD.MM.GGGG.)", "DD.MM.GGGG.", side="left", date_picker=True)
        self.add_field(row, "expiry_date", "Pretplata vrijedi do", "DD.MM.GGGG.", side="right", date_picker=True)
        duration = ctk.CTkFrame(outer, fg_color=COLORS["panel_hover"], corner_radius=9)
        duration.pack(fill="x", pady=(3, 1))
        ctk.CTkLabel(duration, text="Trajanje od kupnje", font=("Arial", 11, "bold"), text_color=COLORS["muted"]).pack(side="left", padx=(10, 5), pady=5)
        self.duration_amount = ctk.CTkEntry(duration, width=48, height=30, justify="center", placeholder_text="1", fg_color=COLORS["input"], border_color=COLORS["border"], text_color=COLORS["text"])
        self.duration_amount.insert(0, "1")
        self.duration_amount.pack(side="left", padx=3, pady=5)
        self.duration_unit = ctk.CTkOptionMenu(duration, values=[tr(value) for value in ("mjesec(i)", "godina(e)")], width=110, height=30, fg_color=COLORS["input"], button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"], text_color=COLORS["text"])
        self.duration_unit.pack(side="left", padx=3, pady=5)
        ctk.CTkButton(duration, text="Jamstvo", command=lambda: WarrantyDurationDialog(self), width=78, height=30, corner_radius=8, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 11, "bold")).pack(side="right", padx=(3, 7), pady=5)
        ctk.CTkButton(duration, text="Postavi datum", command=self.calculate_expiry, width=108, height=30, corner_radius=8, fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=("Arial", 11, "bold")).pack(side="right", padx=7, pady=5)
        row = ctk.CTkFrame(outer, fg_color="transparent")
        row.pack(fill="x", pady=1)
        self.add_field(row, "seller_warranty", "Jamstvo prodavatelja vrijedi do", "DD.MM.GGGG.", side="left", date_picker=True)
        self.add_field(row, "category", "Kategorija", "Streaming, AI, Cloud...", side="right")
        row = ctk.CTkFrame(outer, fg_color="transparent")
        row.pack(fill="x", pady=1)
        self.add_field(row, "seller", "Prodavatelj / gdje je kupljeno", "npr. službena stranica", side="left")
        self.add_field(row, "seller_username", "Korisničko ime prodavatelja", "npr. prodavatelj123", side="right")
        row = ctk.CTkFrame(outer, fg_color="transparent")
        row.pack(fill="x", pady=1)
        self.add_field(row, "purchase_url", "Poveznica na kupnju", "https://...", side="left")
        self.add_field(row, "chat_url", "Poveznica na chat s prodavateljem", "https://...", side="right")
        extras = ctk.CTkFrame(outer, fg_color="transparent")
        extras.pack(fill="x", pady=(4, 2))
        self.subscription_button = ctk.CTkButton(extras, text="↻  Trošak i obnova", command=lambda: SubscriptionOptionsDialog(self), height=34, corner_radius=9,
                                                 fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 11, "bold"))
        self.subscription_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.attachment_button = ctk.CTkButton(extras, text="📎  Dodaj račun / PDF", command=self.add_attachments, height=34, corner_radius=9,
                                               fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 11, "bold"))
        self.attachment_button.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.update_subscription_button()
        self.update_attachment_button()
        ctk.CTkLabel(outer, text="Bilješke", text_color=COLORS["muted"], font=("Arial", 11, "bold")).pack(anchor="w", pady=(3, 1))
        self.notes = ctk.CTkTextbox(outer, height=58, corner_radius=10, fg_color=COLORS["input"], border_width=1, border_color=COLORS["border"], text_color=COLORS["text"])
        self.notes.pack(fill="x")
        ctk.CTkButton(outer, text="Spremi promjene", height=38, corner_radius=10, fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], command=self.save).pack(fill="x", pady=(6, 3))

        if record or self.preset:
            for key, field in self.fields.items():
                if record:
                    value = app.vault.decrypt(record["password"]) if key == "password" else record.get(key, "")
                else:
                    value = self.preset.get(key, "")
                if getattr(field, "is_date_input", False) and value:
                    parsed = parse_date(value)
                    if parsed:
                        self.set_date(field, parsed)
                else:
                    field.insert(0, value)
            if record:
                self.notes.insert("1.0", record.get("notes", ""))

        self.wait_visibility()
        self.grab_set()

    def update_subscription_button(self) -> None:
        price = parse_price(self.subscription_values.get("price", ""))
        if price is None:
            text = f"↻  {tr('Trošak i obnova')}"
        else:
            text = f"↻  {format_money(price, self.subscription_values['currency'])} · {tr(self.subscription_values['billing_cycle'])}"
        self.subscription_button.configure(text=text)

    def update_attachment_button(self) -> None:
        count = len(self.attachments) + len(self.pending_attachments)
        self.attachment_button.configure(text=f"📎  {tr('Privici ({count})').format(count=count)}" if count else f"📎  {tr('Dodaj račun / PDF')}")

    def add_attachments(self) -> None:
        sources = filedialog.askopenfilenames(
            title="Odaberite račun ili PDF", parent=self,
            filetypes=[("Računi i dokumenti", "*.pdf *.png *.jpg *.jpeg *.webp *.txt"), ("Sve datoteke", "*.*")],
        )
        for source in sources:
            if source not in self.pending_attachments:
                self.pending_attachments.append(source)
        self.update_attachment_button()

    def pick_service(self, choice: str) -> None:
        name, category = choice.split("  ·  ", 1)
        self.fields["name"].delete(0, END)
        self.fields["name"].insert(0, name)
        self.fields["category"].delete(0, END)
        self.fields["category"].insert(0, category)
        self.show_hint(f"Odabrano: {name} · {category}")

    def show_hint(self, text: str) -> None:
        for child in self.suggestions.winfo_children():
            child.destroy()
        ctk.CTkLabel(self.suggestions, text=text, font=("Arial", 10), text_color=COLORS["muted"]).pack(anchor="w", pady=4)

    def filter_service_suggestions(self, _event=None) -> None:
        query = self.name_entry.get().casefold().strip()
        for child in self.suggestions.winfo_children():
            child.destroy()
        if not query:
            self.show_hint("Počnite pisati za prijedloge ili upišite vlastitu uslugu.")
            return
        matches = [(name, category) for name, category in self.app.catalog.items() if query in name.casefold() or query in category.casefold()]
        if not matches:
            self.show_hint("Nema podudaranja — možete spremiti vlastitu uslugu.")
            return
        for name, category in matches[:3]:
            ctk.CTkButton(self.suggestions, text=f"{name} · {category}", height=28, corner_radius=7,
                          command=lambda n=name, c=category: self.pick_service(f"{n}  ·  {c}"),
                          fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"],
                          font=("Arial", 10, "bold")).pack(side="left", padx=(0, 4), pady=1)

    def calculate_expiry(self) -> None:
        purchase = parse_date(self.fields["purchase_date"].get())
        try:
            amount = int(self.duration_amount.get())
        except ValueError:
            amount = 0
        if not purchase:
            messagebox.showwarning("Nedostaje datum kupnje", "Najprije odaberite datum kupnje u kalendaru ili ga upišite kao GGGG-MM-DD.", parent=self)
            return
        if not 1 <= amount <= 240:
            messagebox.showwarning("Neispravno trajanje", "Upišite broj od 1 do 240.", parent=self)
            return
        months = amount * (12 if self.duration_unit.get() == tr("godina(e)") else 1)
        expiry = add_months(purchase, months)
        self.set_date(self.fields["expiry_date"], expiry)

    def calculate_warranty(self, amount_text: str, unit: str) -> bool:
        purchase = parse_date(self.fields["purchase_date"].get())
        if not purchase:
            messagebox.showwarning("Nedostaje datum kupnje", "Najprije odaberite datum kupnje u kalendaru.", parent=self)
            return False
        if unit == tr("Cjelokupno trajanje pretplate"):
            warranty = parse_date(self.fields["expiry_date"].get())
            if not warranty:
                messagebox.showwarning("Nedostaje datum isteka", "Najprije postavite datum isteka pretplate.", parent=self)
                return False
        else:
            try:
                amount = int(amount_text)
            except ValueError:
                amount = 0
            if not 1 <= amount <= 2400:
                messagebox.showwarning("Neispravno trajanje", "Upišite broj od 1 do 2400.", parent=self)
                return False
            if unit == tr("dana"):
                warranty = purchase + timedelta(days=amount)
            else:
                months = amount * (12 if unit == tr("godina(e)") else 1)
                warranty = add_months(purchase, months)
        self.set_date(self.fields["seller_warranty"], warranty)
        return True

    @staticmethod
    def set_date(field, value: date) -> None:
        formatted = date_value(value)
        if getattr(field, "is_date_input", False):
            field.date_value = formatted
            field.configure(text=formatted, text_color=COLORS["text"])
            return
        field.delete(0, END)
        field.insert(0, formatted)

    @staticmethod
    def toggle_password(field: ctk.CTkEntry, button: ctk.CTkButton) -> None:
        hidden = bool(field.cget("show"))
        field.configure(show="" if hidden else "●")
        button.configure(text="◉" if hidden else "◌")

    def add_field(self, parent, key, label, placeholder, secret=False, side=None, date_picker=False):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        if side:
            frame.pack(side=side, expand=True, fill="x", padx=(0, 7) if side == "left" else (7, 0))
        else:
            frame.pack(fill="x", pady=4)
        ctk.CTkLabel(frame, text=label, text_color=COLORS["muted"], font=("Arial", 11, "bold")).pack(anchor="w", pady=(1, 1))
        holder = ctk.CTkFrame(frame, fg_color="transparent")
        holder.pack(fill="x")
        if date_picker:
            field = ctk.CTkButton(holder, text=placeholder, anchor="w", height=34, corner_radius=9, border_width=1,
                                  fg_color=COLORS["input"], hover_color=COLORS["panel_hover"], border_color=COLORS["border"],
                                  text_color=COLORS["muted"], font=("Arial", 12))
            field.is_date_input = True
            field.date_value = ""
            field.get = lambda control=field: control.date_value
            field.configure(command=lambda target=field: CalendarPopup(self, target))
        else:
            field = ctk.CTkEntry(holder, placeholder_text=placeholder, height=34, corner_radius=9, show="●" if secret else "",
                                 fg_color=COLORS["input"], border_color=COLORS["border"], text_color=COLORS["text"])
        field.pack(side="left", fill="x", expand=True)
        if secret:
            eye = ctk.CTkButton(holder, text="◌", width=34, height=34, corner_radius=8, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["accent"], font=("Arial", 16, "bold"))
            eye.configure(command=lambda target=field, control=eye: self.toggle_password(target, control))
            eye.pack(side="right", padx=(4, 0))
        self.fields[key] = field

    def save(self):
        values = {key: field.get().strip() for key, field in self.fields.items()}
        if not values["name"]:
            messagebox.showwarning("Nedostaje naziv", "Upišite naziv usluge.", parent=self)
            return
        for key in ("purchase_date", "expiry_date", "seller_warranty"):
            if values[key] and not parse_date(values[key]):
                messagebox.showwarning("Neispravan datum", f"Polje „{key}” mora biti u formatu GGGG-MM-DD.", parent=self)
                return
        for key in ("purchase_url", "chat_url"):
            if values[key] and not values[key].startswith(("https://", "http://")):
                messagebox.showwarning("Neispravna poveznica", "Poveznice moraju početi s https:// ili http://", parent=self)
                return
        if self.subscription_values["price"] and parse_price(self.subscription_values["price"]) is None:
            messagebox.showwarning("Neispravna cijena", "Cijenu upišite kao npr. 9,99.", parent=self)
            return
        if self.subscription_values["renewal_date"] and not parse_date(self.subscription_values["renewal_date"]):
            messagebox.showwarning("Neispravan datum", "Odaberite datum sljedeće naplate u kalendaru.", parent=self)
            return
        current_id = self.record.get("id") if self.record else None
        duplicate = next((item for item in self.app.records if item.get("id") != current_id and item.get("name", "").casefold() == values["name"].casefold()), None)
        if duplicate and not messagebox.askyesno("Moguć duplikat", f"Usluga „{duplicate['name']}” već postoji. Želite li ipak spremiti novi zapis?", parent=self):
            return
        old_password = self.record.get("password", "") if self.record else ""
        values["password"] = self.app.vault.encrypt(values["password"]) if values["password"] else old_password
        values["notes"] = self.notes.get("1.0", "end-1c").strip()
        values["id"] = self.record["id"] if self.record else secrets.token_hex(8)
        values.update(self.subscription_values)
        values["attachments"] = self.attachments.copy()
        try:
            values["attachments"].extend(self.app.vault.save_attachment(source, values["id"]) for source in self.pending_attachments)
        except (OSError, ValueError) as error:
            messagebox.showerror("Privitak nije spremljen", str(error), parent=self)
            return
        self.app.upsert(values)
        self.destroy()


class RecordDetailsDialog(ctk.CTkToplevel):
    """Read-only, at-a-glance view opened by double-clicking a service card."""
    def __init__(self, app: "DigitalVault", record: dict) -> None:
        super().__init__(app)
        self.app, self.record = app, record
        self.title(record["name"])
        if app.app_icon:
            self.iconphoto(True, app.app_icon)
        self.geometry("700x710")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.transient(app)

        outer = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        outer.pack(expand=True, fill="both", padx=24, pady=18)
        title_row = ctk.CTkFrame(outer, fg_color="transparent")
        title_row.pack(fill="x")
        ctk.CTkLabel(title_row, text=record["name"], font=("Arial", 23, "bold"), text_color=COLORS["text"]).pack(side="left")
        status, color = app.status(record)
        ctk.CTkLabel(title_row, text=status, font=("Arial", 11, "bold"), text_color=color, fg_color=COLORS["badge"], corner_radius=7).pack(side="right")
        ctk.CTkLabel(outer, text="Detalji spremljene usluge", font=("Arial", 12), text_color=COLORS["muted"]).pack(anchor="w", pady=(2, 14))

        self.add_pair(outer, "Kategorija", record.get("category", ""), "Prodavatelj", record.get("seller", ""))
        self.add_pair(outer, "Korisničko ime prodavatelja", record.get("seller_username", ""), "Kupljeno", date_text(record.get("purchase_date", "")))
        self.add_pair(outer, "Pretplata vrijedi do", date_text(record.get("expiry_date", "")), "Jamstvo vrijedi do", date_text(record.get("seller_warranty", "")))
        price = parse_price(str(record.get("price", "")))
        price_text = f"{format_money(price, record.get('currency', 'EUR'))} · {tr(record.get('billing_cycle', 'Mjesečno')).lower()}" if price is not None else "—"
        auto_renew = tr("Da") if record.get("auto_renew") == "Da" else tr("Ne")
        if record.get("renewal_date"):
            auto_renew += f" · {date_text(record['renewal_date'])}"
        self.add_pair(outer, "Trošak", price_text, "Automatska obnova", auto_renew)
        self.add_credentials(outer)
        self.add_links(outer)
        self.add_attachments(outer)
        ctk.CTkLabel(outer, text="Bilješke", font=("Arial", 11, "bold"), text_color=COLORS["muted"]).pack(anchor="w", pady=(10, 3))
        notes = ctk.CTkTextbox(outer, height=86, corner_radius=10, fg_color=COLORS["input"], border_width=1, border_color=COLORS["border"], text_color=COLORS["text"])
        notes.pack(fill="x")
        notes.insert("1.0", record.get("notes", "") or "Nema bilješki.")
        notes.configure(state="disabled")
        actions = ctk.CTkFrame(outer, fg_color="transparent")
        actions.pack(fill="x", pady=(13, 2))
        ctk.CTkButton(actions, text="Uredi zapis", command=self.edit, height=38, corner_radius=9, fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=("Arial", 12, "bold")).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(actions, text="Zatvori", command=self.destroy, height=38, corner_radius=9, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"]).pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.wait_visibility()
        self.grab_set()

    def add_pair(self, parent, left_label: str, left_value: str, right_label: str, right_value: str) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)
        self.add_value(row, left_label, left_value, "left")
        self.add_value(row, right_label, right_value, "right")

    def add_value(self, parent, label: str, value: str, side: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color=COLORS["panel"], corner_radius=9)
        frame.pack(side=side, fill="x", expand=True, padx=(0, 5) if side == "left" else (5, 0))
        ctk.CTkLabel(frame, text=label, font=("Arial", 10, "bold"), text_color=COLORS["muted"]).pack(anchor="w", padx=11, pady=(7, 0))
        ctk.CTkLabel(frame, text=value or "—", font=("Arial", 12), text_color=COLORS["text"], anchor="w").pack(fill="x", padx=11, pady=(0, 7))
        return frame

    def add_credentials(self, parent) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)
        login_box = self.add_value(row, "E-mail / korisničko ime", self.record.get("login", ""), "left")
        secret = ctk.CTkFrame(row, fg_color=COLORS["panel"], corner_radius=9)
        secret.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(secret, text="Lozinka", font=("Arial", 10, "bold"), text_color=COLORS["muted"]).pack(anchor="w", padx=11, pady=(7, 0))
        password_row = ctk.CTkFrame(secret, fg_color="transparent")
        password_row.pack(fill="x", padx=11, pady=(0, 5))
        self.password_text = StringVar(value="••••••••" if self.record.get("password") else "—")
        ctk.CTkLabel(password_row, textvariable=self.password_text, font=("Arial", 12), text_color=COLORS["text"]).pack(side="left", fill="x", expand=True)
        if self.record.get("login"):
            ctk.CTkButton(login_box, text="⧉", command=lambda: self.app.copy_to_clipboard(self.record["login"], "Korisničko ime"), width=28, height=24, corner_radius=7,
                          fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["accent"]).pack(anchor="e", padx=8, pady=(0, 6))
        if self.record.get("password"):
            ctk.CTkButton(password_row, text="⧉", command=lambda: self.app.copy_to_clipboard(self.app.vault.decrypt(self.record["password"]), "Lozinka"), width=28, height=25, corner_radius=7,
                          fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["accent"]).pack(side="right", padx=(0, 4))
            self.eye = ctk.CTkButton(password_row, text="◌", command=self.toggle_password, width=30, height=25, corner_radius=7, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["accent"], font=("Arial", 14, "bold"))
            self.eye.pack(side="right")

    def add_links(self, parent) -> None:
        links = ctk.CTkFrame(parent, fg_color="transparent")
        links.pack(fill="x", pady=(10, 0))
        if self.record.get("purchase_url"):
            ctk.CTkButton(links, text="↗ Otvori kupnju", command=lambda: webbrowser.open(self.record["purchase_url"]), height=31, corner_radius=8, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 11, "bold")).pack(side="left", padx=(0, 5))
        if self.record.get("chat_url"):
            ctk.CTkButton(links, text="◌ Otvori chat s prodavateljem", command=lambda: webbrowser.open(self.record["chat_url"]), height=31, corner_radius=8, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 11, "bold")).pack(side="left", padx=5)

    def add_attachments(self, parent) -> None:
        attachments = self.record.get("attachments", [])
        if not attachments:
            return
        ctk.CTkLabel(parent, text="Privici", font=("Arial", 11, "bold"), text_color=COLORS["muted"]).pack(anchor="w", pady=(10, 3))
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x")
        for attachment in attachments[:3]:
            ctk.CTkButton(row, text=f"📎 {attachment.get('name', 'Privitak')}", command=lambda item=attachment: self.open_attachment(item), height=30, corner_radius=8,
                          fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 10)).pack(side="left", padx=(0, 5))
        if len(attachments) > 3:
            ctk.CTkLabel(row, text=f"+{len(attachments) - 3}", font=("Arial", 11, "bold"), text_color=COLORS["muted"]).pack(side="left", padx=5)

    def open_attachment(self, attachment: dict) -> None:
        try:
            self.app.vault.open_attachment(attachment)
        except (OSError, ValueError, InvalidToken) as error:
            messagebox.showerror("Privitak nije moguće otvoriti", str(error), parent=self)

    def toggle_password(self) -> None:
        hidden = self.password_text.get() == "••••••••"
        self.password_text.set(self.app.vault.decrypt(self.record["password"]) if hidden else "••••••••")
        self.eye.configure(text="◉" if hidden else "◌")

    def edit(self) -> None:
        self.destroy()
        RecordDialog(self.app, self.record)


class CatalogEditorDialog(ctk.CTkToplevel):
    """Local editor for both included and user-created catalog entries."""
    def __init__(self, app: "DigitalVault") -> None:
        super().__init__(app)
        self.app, self.selected_name, self.page = app, None, 0
        self.render_job = None
        self.title("Uredi katalog")
        if app.app_icon:
            self.iconphoto(True, app.app_icon)
        self.geometry("690x650")
        self.minsize(610, 540)
        self.configure(fg_color=COLORS["bg"])
        self.search = StringVar()
        self.name = StringVar()
        self.category = StringVar()
        outer = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        outer.pack(expand=True, fill="both", padx=22, pady=18)
        ctk.CTkLabel(outer, text="Uredi katalog", font=("Arial", 22, "bold"), text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(outer, text="Dodajte, promijenite ili uklonite prijedloge. Sve se sprema samo na ovom računalu.",
                     font=("Arial", 12), text_color=COLORS["muted"]).pack(anchor="w", pady=(1, 12))
        form = ctk.CTkFrame(outer, fg_color=COLORS["panel"], corner_radius=12)
        form.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(form, text="Naziv usluge", font=("Arial", 10, "bold"), text_color=COLORS["muted"]).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 1))
        ctk.CTkLabel(form, text="Kategorija", font=("Arial", 10, "bold"), text_color=COLORS["muted"]).grid(row=0, column=1, sticky="w", padx=7, pady=(10, 1))
        name = ctk.CTkEntry(form, textvariable=self.name, placeholder_text="npr. Nova usluga", height=34, corner_radius=8,
                            fg_color=COLORS["input"], border_color=COLORS["border"], text_color=COLORS["text"])
        name.grid(row=1, column=0, sticky="ew", padx=(12, 7), pady=(0, 10))
        category = ctk.CTkEntry(form, textvariable=self.category, placeholder_text="npr. Streaming", height=34, corner_radius=8,
                                fg_color=COLORS["input"], border_color=COLORS["border"], text_color=COLORS["text"])
        category.grid(row=1, column=1, sticky="ew", padx=7, pady=(0, 10))
        ctk.CTkButton(form, text="Spremi stavku", command=self.save_entry, width=110, height=34, corner_radius=8,
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]).grid(row=1, column=2, padx=(7, 12), pady=(0, 10))
        ctk.CTkButton(form, text="Nova", command=self.new_entry, width=58, height=30, corner_radius=8,
                      fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"]).grid(row=2, column=0, sticky="w", padx=12, pady=(0, 10))
        self.delete_button = ctk.CTkButton(form, text="Obriši odabranu", command=self.delete_entry, width=120, height=30, corner_radius=8,
                                           fg_color="transparent", border_width=1, border_color=COLORS["danger"], text_color=COLORS["danger"], hover_color="#3B1E32", state="disabled")
        self.delete_button.grid(row=2, column=2, sticky="e", padx=12, pady=(0, 10))
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)
        search = ctk.CTkEntry(outer, textvariable=self.search, placeholder_text="⌕  Pretraži stavke kataloga...", height=39, corner_radius=9,
                              fg_color=COLORS["input"], border_color=COLORS["border"], text_color=COLORS["text"])
        search.pack(fill="x", pady=(0, 7))
        self.search.trace_add("write", self.reset_page)
        self.count = ctk.CTkLabel(outer, text_color=COLORS["muted"], font=("Arial", 10, "bold"))
        self.count.pack(anchor="w")
        pager = ctk.CTkFrame(outer, fg_color="transparent")
        pager.pack(fill="x", pady=(2, 3))
        self.previous = ctk.CTkButton(pager, text="‹ Prethodno", width=92, height=28, corner_radius=7, command=lambda: self.change_page(-1),
                                      fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"])
        self.previous.pack(side="left")
        self.page_label = ctk.CTkLabel(pager, font=("Arial", 10, "bold"), text_color=COLORS["muted"])
        self.page_label.pack(side="left", expand=True)
        self.next = ctk.CTkButton(pager, text="Sljedeće ›", width=92, height=28, corner_radius=7, command=lambda: self.change_page(1),
                                  fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"])
        self.next.pack(side="right")
        self.listing = ctk.CTkScrollableFrame(outer, fg_color="transparent", scrollbar_button_color=COLORS["border"])
        self.listing.pack(expand=True, fill="both", pady=(3, 0))
        self.render_entries()
        self.wait_visibility()
        self.grab_set()

    def render_entries(self) -> None:
        for child in self.listing.winfo_children():
            child.destroy()
        term = self.search.get().casefold().strip()
        entries = [(name, category) for name, category in self.app.catalog.items()
                   if not term or term in name.casefold() or term in category.casefold()]
        entries.sort(key=lambda item: (item[1].casefold(), item[0].casefold()))
        total_pages = max(1, (len(entries) + CATALOG_PAGE_SIZE - 1) // CATALOG_PAGE_SIZE)
        self.page = min(self.page, total_pages - 1)
        first = self.page * CATALOG_PAGE_SIZE
        visible = entries[first:first + CATALOG_PAGE_SIZE]
        self.count.configure(text=f"{len(entries)} stavki · kliknite stavku za uređivanje")
        self.page_label.configure(text=f"Stranica {self.page + 1} / {total_pages}")
        self.previous.configure(state="normal" if self.page else "disabled")
        self.next.configure(state="normal" if self.page < total_pages - 1 else "disabled")
        for entry_name, entry_category in visible:
            selected = entry_name == self.selected_name
            row = ctk.CTkButton(self.listing, text=f"{entry_name}    ·    {entry_category}", anchor="w", height=34, corner_radius=8,
                                fg_color=COLORS["sidebar_card"] if selected else COLORS["panel"], hover_color=COLORS["panel_hover"],
                                text_color=COLORS["text"], command=lambda n=entry_name: self.select_entry(n))
            row.pack(fill="x", pady=2)

    def reset_page(self, *_args) -> None:
        self.page = 0
        if self.render_job:
            self.after_cancel(self.render_job)
        self.render_job = self.after(120, self.render_after_search)

    def render_after_search(self) -> None:
        self.render_job = None
        self.render_entries()

    def change_page(self, amount: int) -> None:
        self.page = max(0, self.page + amount)
        self.render_entries()

    def select_entry(self, name: str) -> None:
        self.selected_name = name
        self.name.set(name)
        self.category.set(self.app.catalog.get(name, ""))
        self.delete_button.configure(state="normal")
        self.render_entries()

    def new_entry(self) -> None:
        self.selected_name = None
        self.name.set("")
        self.category.set("")
        self.delete_button.configure(state="disabled")

    def save_entry(self) -> None:
        name, category = self.name.get().strip(), self.category.get().strip()
        if not name or not category:
            messagebox.showwarning("Nedostaju podaci", "Upišite naziv usluge i kategoriju.", parent=self)
            return
        duplicate = next((item for item in self.app.catalog if item.casefold() == name.casefold() and item != self.selected_name), None)
        if duplicate and not messagebox.askyesno("Postojeća usluga", f"„{duplicate}” već postoji. Zamijeniti njezinu kategoriju?", parent=self):
            return
        if self.selected_name and self.selected_name != name:
            self.app.catalog.pop(self.selected_name, None)
        if duplicate and duplicate != name:
            self.app.catalog.pop(duplicate, None)
        self.app.catalog[name] = category
        self.app.vault.save_catalog(self.app.catalog)
        self.selected_name = name
        self.delete_button.configure(state="normal")
        self.app.refresh()
        self.render_entries()

    def delete_entry(self) -> None:
        if not self.selected_name:
            return
        if not messagebox.askyesno("Obriši stavku", f"Ukloniti „{self.selected_name}” iz kataloga?", parent=self):
            return
        self.app.catalog.pop(self.selected_name, None)
        self.app.vault.save_catalog(self.app.catalog)
        self.app.refresh()
        self.new_entry()
        self.render_entries()


class RemindersDialog(ctk.CTkToplevel):
    def __init__(self, app: "DigitalVault") -> None:
        super().__init__(app)
        self.app = app
        self.title(tr("Podsjetnici"))
        if app.app_icon:
            self.iconphoto(True, app.app_icon)
        self.geometry("650x540")
        self.minsize(560, 440)
        self.configure(fg_color=COLORS["bg"])
        outer = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        outer.pack(expand=True, fill="both", padx=22, pady=18)
        ctk.CTkLabel(outer, text="Podsjetnici", font=("Arial", 22, "bold"), text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(outer, text="Rokovi koje ste označili za podsjetnik.", font=("Arial", 12), text_color=COLORS["muted"]).pack(anchor="w", pady=(1, 12))
        listing = ctk.CTkScrollableFrame(outer, fg_color="transparent", scrollbar_button_color=COLORS["border"])
        listing.pack(expand=True, fill="both")
        reminders = app.reminders()
        if not reminders:
            ctk.CTkLabel(listing, text="Nema nadolazećih podsjetnika.", font=("Arial", 14), text_color=COLORS["muted"]).pack(expand=True, pady=80)
        for record, label, deadline, days in reminders:
            card = ctk.CTkFrame(listing, fg_color=COLORS["panel"], corner_radius=11)
            card.pack(fill="x", pady=4)
            ctk.CTkLabel(card, text=record.get("name", "Usluga"), font=("Arial", 14, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=13, pady=(10, 0))
            text = f"{label}: {date_text(deadline)}" + (" · danas" if days == 0 else f" · za {days} dana")
            ctk.CTkLabel(card, text=text, font=("Arial", 11), text_color=COLORS["warning"] if days <= 7 else COLORS["muted"]).pack(anchor="w", padx=13, pady=(1, 10))
        ctk.CTkButton(outer, text="Zatvori", command=self.destroy, height=37, corner_radius=9, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"]).pack(fill="x", pady=(12, 0))
        self.wait_visibility()
        self.grab_set()


class DigitalVault(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.vault, self.records = Vault(), []
        self.app_icon = None
        self.language = self.vault.language() if self.vault.initialized else "en"
        global CURRENT_LANGUAGE
        CURRENT_LANGUAGE = self.language
        self.theme = self.vault.theme() if self.vault.initialized else "dark"
        self.apply_theme(self.theme)
        self.selected_id: str | None = None
        self.active_page = "overview"
        self.search = StringVar()
        self.category_filter = StringVar(value=tr("Sve kategorije"))
        self.status_filter = StringVar(value=tr("Sve usluge"))
        self.catalog_search = StringVar()
        self.catalog_category_filter = StringVar(value=tr("Sve vrste"))
        self.catalog_page = 0
        self.catalog_render_job = None
        self.update_button = None
        self.updater = SelfUpdater(self, APP_VERSION, GITHUB_REPO, lambda: self.update_button, lambda: self.language)
        self.search.trace_add("write", self.on_overview_search)
        self.catalog_search.trace_add("write", self.reset_catalog_page)
        self.title(tr("Digitalni sef"))
        self.geometry("1180x730")
        self.minsize(980, 620)
        self.configure(fg_color=COLORS["bg"])
        self.withdraw()
        self.after(50, lambda: SplashScreen(self))

    def apply_theme(self, theme: str) -> None:
        self.theme = theme if theme in ("dark", "light") else "dark"
        COLORS.clear()
        COLORS.update(LIGHT_COLORS if self.theme == "light" else DARK_COLORS)
        ctk.set_appearance_mode(self.theme)
        self.load_theme_icon()

    def load_theme_icon(self) -> None:
        try:
            self.app_icon = PhotoImage(file=str(ICON_FILES[self.theme]))
            self.iconphoto(True, self.app_icon)
        except (TclError, OSError):
            self.app_icon = None

    def toggle_theme(self) -> None:
        self.apply_theme("light" if self.theme == "dark" else "dark")
        self.vault.save_theme(self.theme)
        self.configure(fg_color=COLORS["bg"])
        for widget in self.winfo_children():
            widget.destroy()
        self.build_ui()
        self.refresh()
        self.after(1400, lambda: self.updater.check(manual=False))

    def set_language(self, label: str) -> None:
        self.language = "en" if label in ("English", "en") else "hr"
        global CURRENT_LANGUAGE
        CURRENT_LANGUAGE = self.language
        self.vault.save_language(self.language)
        self.category_filter.set(tr("Sve kategorije"))
        self.status_filter.set(tr("Sve usluge"))
        self.catalog_category_filter.set(tr("Sve vrste"))
        self.title(tr("Digitalni sef"))
        for widget in self.winfo_children():
            widget.destroy()
        self.build_ui()
        self.refresh()

    def start(self):
        self.records = self.vault.load()
        self.catalog = self.vault.load_catalog()
        self.deiconify()
        self.build_ui()
        self.refresh()

    def on_overview_search(self, *_args) -> None:
        if self.active_page == "overview" and hasattr(self, "listing"):
            self.render_cards()

    def reset_catalog_page(self, *_args) -> None:
        self.catalog_page = 0
        if self.active_page == "catalog" and hasattr(self, "catalog_listing"):
            if self.catalog_render_job:
                self.after_cancel(self.catalog_render_job)
            self.catalog_render_job = self.after(120, self.render_catalog_after_search)

    def render_catalog_after_search(self) -> None:
        self.catalog_render_job = None
        if self.active_page == "catalog" and hasattr(self, "catalog_listing"):
            self.render_catalog()

    def build_ui(self):
        sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=COLORS["sidebar"])
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ctk.CTkLabel(sidebar, text=f"◈  {tr('Digitalni sef')}", font=("Arial", 21, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=25, pady=(33, 3))
        ctk.CTkLabel(sidebar, text="Vaši digitalni računi na jednom mjestu", font=("Arial", 11), text_color=COLORS["muted"]).pack(anchor="w", padx=25, pady=(0, 34))
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        for key, icon, text in [("overview", "▦", "Pregled"), ("catalog", "▤", "Katalog usluga"), ("costs", "◫", "Troškovi")]:
            button = ctk.CTkButton(sidebar, text=f"{icon}  {tr(text)}", command=lambda page=key: self.show_page(page), height=39,
                                   corner_radius=9, anchor="w", font=("Arial", 12, "bold"), text_color=COLORS["text"])
            button.pack(fill="x", padx=17, pady=3)
            self.nav_buttons[key] = button
        ctk.CTkLabel(sidebar, text="Jezik", font=("Arial", 10, "bold"), text_color=COLORS["muted"]).pack(anchor="w", padx=18, pady=(18, 3))
        language_choices = [tr("Hrvatski"), "English"]
        self.language_menu = ctk.CTkOptionMenu(sidebar, values=language_choices, command=self.set_language, height=35, corner_radius=9,
                                               fg_color=COLORS["panel_hover"], button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"], text_color=COLORS["text"])
        self.language_menu.pack(fill="x", padx=17, pady=(0, 12))
        self.language_menu.set("English" if self.language == "en" else tr("Hrvatski"))
        self.reminder_button = ctk.CTkButton(sidebar, text=f"⚠  {tr('Podsjetnici')}", command=lambda: RemindersDialog(self), height=38, corner_radius=9,
                                             fg_color=COLORS["sidebar_card"], hover_color=COLORS["panel_hover"], text_color=COLORS["text"], font=("Arial", 12, "bold"))
        self.reminder_button.pack(side="bottom", fill="x", padx=17, pady=(0, 10))
        self.update_button = ctk.CTkButton(sidebar, text=f"↻  {tr('Provjeri ažuriranja')}", command=self.updater.check, height=35, corner_radius=9,
                                           fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 11, "bold"))
        self.update_button.pack(side="bottom", fill="x", padx=17, pady=(0, 7))
        ctk.CTkButton(sidebar, text=f"↧  {tr('Vrati kopiju')}", command=self.restore_backup, height=35, corner_radius=9,
                      fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 11, "bold")).pack(side="bottom", fill="x", padx=17, pady=(0, 7))
        ctk.CTkButton(sidebar, text=f"↥  {tr('Sigurnosna kopija')}", command=self.create_backup, height=35, corner_radius=9,
                      fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 11, "bold")).pack(side="bottom", fill="x", padx=17, pady=(0, 7))
        ctk.CTkButton(sidebar, text=f"☀  {tr('Svijetla tema')}" if self.theme == "dark" else f"◐  {tr('Tamna tema')}", command=self.toggle_theme,
                      height=38, corner_radius=9, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 12, "bold")).pack(side="bottom", fill="x", padx=17, pady=(0, 10))
        ctk.CTkButton(sidebar, text="♥  Doniraj putem PayPala", command=lambda: webbrowser.open(PAYPAL_DONATION_URL),
                      height=38, corner_radius=9, fg_color="#0070BA", hover_color="#005EA6", text_color="#FFFFFF", font=("Arial", 12, "bold")).pack(side="bottom", fill="x", padx=17, pady=(0, 10))
        security = ctk.CTkFrame(sidebar, fg_color=COLORS["sidebar_card"], corner_radius=12)
        security.pack(side="bottom", fill="x", padx=17, pady=22)
        ctk.CTkLabel(security, text="🔒  Lokalno šifrirano", font=("Arial", 12, "bold"), text_color=COLORS["success"]).pack(anchor="w", padx=13, pady=(12, 2))
        ctk.CTkLabel(security, text="Lozinke se ne šalju nikamo.", font=("Arial", 10), text_color=COLORS["muted"]).pack(anchor="w", padx=13, pady=(0, 12))

        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.content.pack(side="left", expand=True, fill="both", padx=28, pady=25)
        self.show_page(self.active_page)

    def show_page(self, page: str) -> None:
        self.active_page = page if page in ("overview", "catalog", "costs") else "overview"
        for key, button in self.nav_buttons.items():
            selected = key == self.active_page
            button.configure(fg_color=COLORS["sidebar_card"] if selected else "transparent",
                             hover_color=COLORS["panel_hover"], text_color=COLORS["text"] if selected else COLORS["muted"])
        for child in self.content.winfo_children():
            child.destroy()
        if self.active_page == "catalog":
            self.build_catalog_page()
        elif self.active_page == "costs":
            self.build_costs_page()
        else:
            self.build_overview_page()
            self.update_filter_options()
            self.render_stats()
            self.render_cards()

    def build_overview_page(self) -> None:
        main = self.content
        top = ctk.CTkFrame(main, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text="Moje usluge", font=("Arial", 28, "bold"), text_color=COLORS["text"]).pack(side="left")
        ctk.CTkButton(top, text=f"＋  {tr('Dodaj uslugu')}", command=lambda: RecordDialog(self), width=160, height=42, corner_radius=10, fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=("Arial", 13, "bold")).pack(side="right")
        ctk.CTkLabel(main, text="Pretplate, računi i jamstva prodavatelja na jednom sigurnom mjestu.", font=("Arial", 13), text_color=COLORS["muted"]).pack(anchor="w", pady=(2, 18))
        self.stats = ctk.CTkFrame(main, fg_color="transparent")
        self.stats.pack(fill="x", pady=(0, 17))
        controls = ctk.CTkFrame(main, fg_color="transparent")
        controls.pack(fill="x", pady=(0, 14))
        search = ctk.CTkEntry(controls, textvariable=self.search, placeholder_text=f"⌕  {tr('Pretraži usluge, prodavatelja ili kategoriju...')}", height=42, corner_radius=10, fg_color=COLORS["input"], border_color=COLORS["border"], text_color=COLORS["text"])
        search.pack(side="left", fill="x", expand=True)
        self.category_menu = ctk.CTkOptionMenu(controls, variable=self.category_filter, values=[tr("Sve kategorije")], command=lambda _value: self.render_cards(), width=145, height=42,
                                               fg_color=COLORS["panel_hover"], button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"], text_color=COLORS["text"])
        self.category_menu.pack(side="left", padx=(10, 0))
        self.status_menu = ctk.CTkOptionMenu(controls, variable=self.status_filter, values=[tr(value) for value in ("Sve usluge", "Istječe uskoro", "Isteklo", "Automatska obnova")], command=lambda _value: self.render_cards(), width=160, height=42,
                                             fg_color=COLORS["panel_hover"], button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"], text_color=COLORS["text"])
        self.status_menu.pack(side="left", padx=(8, 0))
        ctk.CTkButton(controls, text="Sve", width=58, height=42, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], command=self.clear_filters).pack(side="left", padx=(8, 0))
        self.listing = ctk.CTkScrollableFrame(main, fg_color="transparent", scrollbar_button_color=COLORS["border"])
        self.listing.pack(expand=True, fill="both")

    def build_catalog_page(self) -> None:
        top = ctk.CTkFrame(self.content, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=tr("Istražite usluge"), font=("Arial", 28, "bold"), text_color=COLORS["text"]).pack(side="left")
        ctk.CTkButton(top, text=f"＋  {tr('Dodaj uslugu')}", command=lambda: RecordDialog(self), width=160, height=42, corner_radius=10,
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=("Arial", 13, "bold")).pack(side="right")
        ctk.CTkButton(top, text="✎  Uredi katalog", command=lambda: CatalogEditorDialog(self), width=145, height=42, corner_radius=10,
                      fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 12, "bold")).pack(side="right", padx=(0, 8))
        ctk.CTkLabel(self.content, text=tr("Odaberite uslugu i otvorit ćemo obrazac s već popunjenim nazivom i kategorijom."),
                     font=("Arial", 13), text_color=COLORS["muted"]).pack(anchor="w", pady=(2, 18))
        controls = ctk.CTkFrame(self.content, fg_color="transparent")
        controls.pack(fill="x", pady=(0, 14))
        search = ctk.CTkEntry(controls, textvariable=self.catalog_search, placeholder_text="⌕  Pretraži katalog usluga...", height=42, corner_radius=10,
                              fg_color=COLORS["input"], border_color=COLORS["border"], text_color=COLORS["text"])
        search.pack(side="left", fill="x", expand=True)
        categories = [tr("Sve vrste"), *sorted(set(self.catalog.values()), key=str.casefold)]
        self.catalog_category_menu = ctk.CTkOptionMenu(controls, variable=self.catalog_category_filter, values=categories,
                                                        command=lambda _value: self.render_catalog(), width=170, height=42,
                                                        fg_color=COLORS["panel_hover"], button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"], text_color=COLORS["text"])
        self.catalog_category_menu.pack(side="left", padx=(10, 0))
        ctk.CTkButton(controls, text=tr("Sve"), width=58, height=42, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"],
                      command=self.clear_catalog_filters).pack(side="left", padx=(8, 0))
        self.catalog_count = ctk.CTkLabel(self.content, text_color=COLORS["muted"], font=("Arial", 11, "bold"))
        self.catalog_count.pack(anchor="w", pady=(0, 4))
        pager = ctk.CTkFrame(self.content, fg_color="transparent")
        pager.pack(fill="x", pady=(0, 4))
        self.catalog_previous = ctk.CTkButton(pager, text="‹ Prethodno", width=92, height=28, corner_radius=7, command=lambda: self.change_catalog_page(-1),
                                              fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"])
        self.catalog_previous.pack(side="left")
        self.catalog_page_label = ctk.CTkLabel(pager, font=("Arial", 10, "bold"), text_color=COLORS["muted"])
        self.catalog_page_label.pack(side="left", expand=True)
        self.catalog_next = ctk.CTkButton(pager, text="Sljedeće ›", width=92, height=28, corner_radius=7, command=lambda: self.change_catalog_page(1),
                                          fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"])
        self.catalog_next.pack(side="right")
        self.catalog_listing = ctk.CTkScrollableFrame(self.content, fg_color="transparent", scrollbar_button_color=COLORS["border"])
        self.catalog_listing.pack(expand=True, fill="both")
        self.render_catalog()

    def clear_catalog_filters(self) -> None:
        self.catalog_search.set("")
        self.catalog_category_filter.set(tr("Sve vrste"))
        self.catalog_page = 0
        self.render_catalog()

    def change_catalog_page(self, amount: int) -> None:
        self.catalog_page = max(0, self.catalog_page + amount)
        self.render_catalog()

    def render_catalog(self) -> None:
        if not hasattr(self, "catalog_listing"):
            return
        for child in self.catalog_listing.winfo_children():
            child.destroy()
        term = self.catalog_search.get().casefold().strip()
        categories = [tr("Sve vrste"), *sorted(set(self.catalog.values()), key=str.casefold)]
        if self.catalog_category_filter.get() not in categories:
            self.catalog_category_filter.set(tr("Sve vrste"))
        self.catalog_category_menu.configure(values=categories)
        category = self.catalog_category_filter.get()
        entries = [(name, group) for name, group in self.catalog.items()
                   if (not term or term in name.casefold() or term in group.casefold())
                   and (category == tr("Sve vrste") or group == category)]
        entries.sort(key=lambda item: (item[1].casefold(), item[0].casefold()))
        total_pages = max(1, (len(entries) + CATALOG_PAGE_SIZE - 1) // CATALOG_PAGE_SIZE)
        self.catalog_page = min(self.catalog_page, total_pages - 1)
        first = self.catalog_page * CATALOG_PAGE_SIZE
        visible = entries[first:first + CATALOG_PAGE_SIZE]
        self.catalog_count.configure(text=f"{len(entries)} {tr('Pronađeno usluga')} · {first + 1 if entries else 0}–{min(first + CATALOG_PAGE_SIZE, len(entries))} od {len(entries)}")
        self.catalog_page_label.configure(text=f"Stranica {self.catalog_page + 1} / {total_pages}")
        self.catalog_previous.configure(state="normal" if self.catalog_page else "disabled")
        self.catalog_next.configure(state="normal" if self.catalog_page < total_pages - 1 else "disabled")
        if not entries:
            ctk.CTkLabel(self.catalog_listing, text="◌  Nema usluga za odabrani filter.", font=("Arial", 14), text_color=COLORS["muted"]).pack(pady=70)
            return
        saved = {record.get("name", "").casefold() for record in self.records}
        for name, group in visible:
            row = ctk.CTkFrame(self.catalog_listing, fg_color=COLORS["panel"], corner_radius=11, border_width=1, border_color=COLORS["border"])
            row.pack(fill="x", pady=4, padx=2)
            ctk.CTkLabel(row, text=name, font=("Arial", 14, "bold"), text_color=COLORS["text"]).pack(side="left", padx=(14, 8), pady=11)
            ctk.CTkLabel(row, text=group, font=("Arial", 11, "bold"), text_color=COLORS["accent"], fg_color=COLORS["badge"], corner_radius=7).pack(side="left", pady=9)
            if name.casefold() in saved:
                ctk.CTkLabel(row, text="✓ Dodano", font=("Arial", 10, "bold"), text_color=COLORS["success"]).pack(side="right", padx=(5, 9))
            ctk.CTkButton(row, text=tr("Dodaj"), width=70, height=29, corner_radius=7, fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                          command=lambda n=name, g=group: RecordDialog(self, preset={"name": n, "category": g})).pack(side="right", padx=12, pady=7)

    def build_costs_page(self) -> None:
        main = ctk.CTkScrollableFrame(self.content, fg_color="transparent", scrollbar_button_color=COLORS["border"])
        main.pack(expand=True, fill="both")
        ctk.CTkLabel(main, text=tr("Pregled potrošnje"), font=("Arial", 28, "bold"), text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(main, text=tr("Procijenjeni trošak na temelju unesenih pretplata."), font=("Arial", 13), text_color=COLORS["muted"]).pack(anchor="w", pady=(2, 18))
        monthly: dict[str, float] = {}
        yearly: dict[str, float] = {}
        one_time: dict[str, float] = {}
        by_category: dict[tuple[str, str], float] = {}
        active = 0
        for record in self.records:
            amount = parse_price(str(record.get("price", "")))
            if amount is None:
                continue
            currency, cycle = record.get("currency", "EUR"), record.get("billing_cycle", "Mjesečno")
            if cycle == "Jednokratno":
                one_time[currency] = one_time.get(currency, 0) + amount
                continue
            active += 1
            per_month = amount / 12 if cycle == "Godišnje" else amount
            monthly[currency] = monthly.get(currency, 0) + per_month
            yearly[currency] = yearly.get(currency, 0) + per_month * 12
            key = (record.get("category", "Ostalo") or "Ostalo", currency)
            by_category[key] = by_category.get(key, 0) + per_month
        def total(values: dict[str, float]) -> str:
            return " · ".join(format_money(value, currency) for currency, value in values.items()) or "—"
        metrics = ctk.CTkFrame(main, fg_color="transparent")
        metrics.pack(fill="x", pady=(0, 18))
        for title, value, color in [("MJESEČNO", total(monthly), COLORS["success"]), ("GODIŠNJE", total(yearly), COLORS["accent"]),
                                    ("JEDNOKRATNE KUPOVINE", total(one_time), COLORS["warning"]), ("Aktivne pretplate", str(active), COLORS["text"])]:
            card = ctk.CTkFrame(metrics, fg_color=COLORS["panel"], corner_radius=13)
            card.pack(side="left", expand=True, fill="x", padx=(0, 10))
            ctk.CTkLabel(card, text=tr(title), font=("Arial", 10, "bold"), text_color=COLORS["muted"]).pack(anchor="w", padx=15, pady=(13, 0))
            ctk.CTkLabel(card, text=value, font=("Arial", 18, "bold"), text_color=color).pack(anchor="w", padx=15, pady=(0, 13))
        ctk.CTkLabel(main, text=tr("Potrošnja po kategoriji"), font=("Arial", 18, "bold"), text_color=COLORS["text"]).pack(anchor="w", pady=(2, 8))
        if not by_category:
            ctk.CTkLabel(main, text=tr("Nema unesenih cijena za prikaz."), font=("Arial", 13), text_color=COLORS["muted"]).pack(anchor="w", pady=14)
            return
        for (category, currency), amount in sorted(by_category.items(), key=lambda item: item[1], reverse=True):
            row = ctk.CTkFrame(main, fg_color=COLORS["panel"], corner_radius=11, border_width=1, border_color=COLORS["border"])
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=category, font=("Arial", 14, "bold"), text_color=COLORS["text"]).pack(side="left", padx=15, pady=12)
            ctk.CTkLabel(row, text=f"{format_money(amount, currency)} / {tr('Mjesečno').lower()}", font=("Arial", 13, "bold"), text_color=COLORS["success"]).pack(side="right", padx=15, pady=12)

    def upsert(self, record: dict):
        found = next((i for i, item in enumerate(self.records) if item["id"] == record["id"]), None)
        if found is None:
            self.records.append(record)
        else:
            self.records[found] = record
        self.vault.save(self.records)
        self.refresh()

    def refresh(self):
        self.update_filter_options()
        if self.active_page == "overview":
            self.render_stats()
            self.render_cards()
        elif self.active_page == "catalog":
            self.render_catalog()
        elif self.active_page == "costs":
            self.show_page("costs")

    def clear_filters(self) -> None:
        self.search.set("")
        self.category_filter.set(tr("Sve kategorije"))
        self.status_filter.set(tr("Sve usluge"))
        self.render_cards()

    def update_filter_options(self) -> None:
        categories = sorted({record.get("category", "").strip() for record in self.records if record.get("category", "").strip()}, key=str.casefold)
        values = [tr("Sve kategorije"), *categories]
        if self.category_filter.get() not in values:
            self.category_filter.set(tr("Sve kategorije"))
        if self.active_page == "overview" and hasattr(self, "category_menu"):
            self.category_menu.configure(values=values)
        reminder_count = len(self.reminders())
        self.reminder_button.configure(text=f"⚠  {tr('Podsjetnici')} ({reminder_count})" if reminder_count else f"⚠  {tr('Podsjetnici')}")

    def reminders(self) -> list[tuple[dict, str, str, int]]:
        today = date.today()
        result = []
        for record in self.records:
            try:
                reminder_days = int(record.get("reminder_days", "7"))
            except (TypeError, ValueError):
                reminder_days = 0
            if reminder_days <= 0:
                continue
            deadlines = [("Pretplata istječe", record.get("expiry_date", "")), ("Jamstvo istječe", record.get("seller_warranty", ""))]
            if record.get("auto_renew") == "Da":
                deadlines.append(("Sljedeća naplata", record.get("renewal_date", "")))
            for label, value in deadlines:
                deadline = parse_date(value)
                if deadline:
                    days = (deadline - today).days
                    if 0 <= days <= reminder_days:
                        result.append((record, label, value, days))
        return sorted(result, key=lambda item: parse_date(item[2]) or date.max)

    def create_backup(self) -> None:
        target = filedialog.asksaveasfilename(title="Spremi šifriranu sigurnosnu kopiju", parent=self, initialdir=APP_DIR,
                                              initialfile=f"digitalni-sef-{date.today().isoformat()}.backup", defaultextension=".backup",
                                              filetypes=[("Digitalni sef sigurnosna kopija", "*.backup"), ("Sve datoteke", "*.*")])
        if not target:
            return
        try:
            self.vault.export_backup(target, self.records)
        except (OSError, ValueError) as error:
            messagebox.showerror("Kopija nije spremljena", str(error), parent=self)
            return
        messagebox.showinfo("Sigurnosna kopija spremljena", "Kopija je šifrirana vašom glavnom lozinkom.", parent=self)

    def restore_backup(self) -> None:
        source = filedialog.askopenfilename(title="Odaberite sigurnosnu kopiju", parent=self, initialdir=APP_DIR,
                                            filetypes=[("Digitalni sef sigurnosna kopija", "*.backup"), ("Sve datoteke", "*.*")])
        if not source:
            return
        if not messagebox.askyesno("Vrati sigurnosnu kopiju", "Zamijeniti sve trenutačne zapise sadržajem odabrane kopije?", icon="warning", parent=self):
            return
        try:
            records, attachments = self.vault.import_backup(source)
            self.vault.restore_attachments(attachments)
        except (OSError, ValueError, KeyError, InvalidToken) as error:
            messagebox.showerror("Kopiju nije moguće vratiti", "Kopija je oštećena ili pripada drugoj glavnoj lozinci.\n\n" + str(error), parent=self)
            return
        self.records = records
        self.vault.save(self.records)
        self.refresh()
        messagebox.showinfo("Kopija vraćena", "Zapisi i šifrirani privici su vraćeni.", parent=self)

    def copy_to_clipboard(self, value: str, label: str) -> None:
        if not value or value.startswith("[nije moguće"):
            messagebox.showwarning("Nema podataka", f"{label} nije dostupan za kopiranje.", parent=self)
            return
        self.clipboard_clear()
        self.clipboard_append(value)
        self.update()
        messagebox.showinfo("Kopirano", f"{label} je kopiran u međuspremnik.", parent=self)

    def render_stats(self):
        for widget in self.stats.winfo_children(): widget.destroy()
        today, near = date.today(), date.today() + timedelta(days=30)
        valid_expiries = [parse_date(r.get("expiry_date", "")) for r in self.records]
        expiring = sum(1 for d in valid_expiries if d and today <= d <= near)
        expired = sum(1 for d in valid_expiries if d and d < today)
        monthly_totals: dict[str, float] = {}
        for record in self.records:
            amount = monthly_amount(record)
            if amount is not None:
                currency = record.get("currency", "EUR")
                monthly_totals[currency] = monthly_totals.get(currency, 0) + amount
        monthly_text = " · ".join(format_money(amount, currency) for currency, amount in monthly_totals.items()) or "—"
        for title, number, tone in [("UKUPNO USLUGA", str(len(self.records)), COLORS["accent"]), ("MJ. TROŠAK", monthly_text, COLORS["success"]), ("ISTJEČE U 30 DANA", str(expiring), COLORS["warning"]), ("ISTEKLO", str(expired), COLORS["danger"])]:
            card = ctk.CTkFrame(self.stats, fg_color=COLORS["panel"], corner_radius=13)
            card.pack(side="left", expand=True, fill="x", padx=(0, 10))
            ctk.CTkLabel(card, text=title, font=("Arial", 10, "bold"), text_color=COLORS["muted"]).pack(anchor="w", padx=15, pady=(13, 0))
            ctk.CTkLabel(card, text=number, font=("Arial", 18 if title == "MJ. TROŠAK" else 24, "bold"), text_color=tone).pack(anchor="w", padx=15, pady=(0, 13))

    def status(self, record: dict):
        renewal = parse_date(record.get("renewal_date", "")) if record.get("auto_renew") == "Da" else None
        expiry = renewal or parse_date(record.get("expiry_date", ""))
        if not expiry: return tr("Nema roka"), COLORS["muted"]
        days = (expiry - date.today()).days
        if days < 0: return tr("Isteklo prije {days} d.").format(days=abs(days)), COLORS["danger"]
        action = tr("Naplata") if renewal else tr("Istječe")
        if days == 0: return tr("{action} danas").format(action=action), COLORS["danger"]
        if days <= 30: return tr("{action} za {days} d.").format(action=action, days=days), COLORS["warning"]
        return tr("{action}: {date}").format(action=action, date=date_text(date_value(expiry))), COLORS["success"]

    def render_cards(self):
        for widget in self.listing.winfo_children(): widget.destroy()
        term = self.search.get().casefold().strip()
        today, near = date.today(), date.today() + timedelta(days=30)
        filtered = []
        for record in self.records:
            searchable = " ".join(str(record.get(key, "")) for key in ("name", "category", "seller", "login"))
            expiry = parse_date(record.get("expiry_date", ""))
            status = self.status_filter.get()
            matches_status = (
                status == tr("Sve usluge")
                or (status == tr("Istječe uskoro") and bool(expiry and today <= expiry <= near))
                or (status == tr("Isteklo") and bool(expiry and expiry < today))
                or (status == tr("Automatska obnova") and record.get("auto_renew") == "Da")
            )
            if (not term or term in searchable.casefold()) and (self.category_filter.get() == tr("Sve kategorije") or record.get("category", "") == self.category_filter.get()) and matches_status:
                filtered.append(record)
        filtered.sort(key=lambda r: parse_date(r.get("expiry_date", "")) or date.max)
        if not filtered:
            text = "Još nema spremljenih usluga." if not self.records else "Nema rezultata za ovu pretragu."
            empty_message = "◌  " + text + "  Dodajte prvu uslugu ili promijenite pretragu."
            ctk.CTkLabel(self.listing, text=empty_message, justify="center", font=("Arial", 14), text_color=COLORS["muted"]).pack(expand=True, pady=80)
            return
        for record in filtered:
            self.card(record)

    def card(self, record: dict):
        card = ctk.CTkFrame(self.listing, fg_color=COLORS["panel"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=6, padx=2)
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=17, pady=(14, 4))
        name_label = ctk.CTkLabel(head, text=record["name"], font=("Arial", 17, "bold"), text_color=COLORS["text"])
        name_label.pack(side="left")
        status, color = self.status(record)
        status_label = ctk.CTkLabel(head, text=status, font=("Arial", 11, "bold"), text_color=color, fg_color=COLORS["badge"], corner_radius=7)
        status_label.pack(side="right")
        seller = record.get("seller", "")
        seller_username = record.get("seller_username", "")
        seller_detail = f"{seller} ({seller_username})" if seller and seller_username else seller or seller_username
        price = parse_price(str(record.get("price", "")))
        cost = f"{format_money(price, record.get('currency', 'EUR'))} / {tr(record.get('billing_cycle', 'Mjesečno')).lower()}" if price is not None else ""
        detail = "  •  ".join(x for x in [record.get("category", ""), record.get("login", ""), cost, seller_detail] if x) or "Nema dodatnih podataka"
        detail_label = ctk.CTkLabel(card, text=detail, font=("Arial", 12), text_color=COLORS["muted"], anchor="w")
        detail_label.pack(fill="x", padx=17)
        password_row = ctk.CTkFrame(card, fg_color="transparent")
        password_row.pack(fill="x", padx=17, pady=(5, 0))
        password_value = StringVar(value="Lozinka: ••••••••" if record.get("password") else "Lozinka nije spremljena")
        ctk.CTkLabel(password_row, textvariable=password_value, font=("Arial", 11), text_color=COLORS["muted"]).pack(side="left")
        if record.get("password"):
            eye = ctk.CTkButton(password_row, text="◌", width=30, height=25, corner_radius=7, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["accent"], font=("Arial", 14, "bold"))
            eye.configure(command=lambda item=record, value=password_value, button=eye: self.toggle_card_password(item, value, button))
            eye.pack(side="left", padx=7)
        action = ctk.CTkFrame(card, fg_color="transparent")
        action.pack(fill="x", padx=14, pady=(9, 12))
        for label, url in [("↗ Kupnja", record.get("purchase_url", "")), ("◌ Chat", record.get("chat_url", ""))]:
            if url:
                ctk.CTkButton(action, text=label, command=lambda link=url: webbrowser.open(link), height=29, width=84, corner_radius=7, fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 11)).pack(side="left", padx=3)
        if record.get("login"):
            ctk.CTkButton(action, text="⧉ E-mail", command=lambda value=record["login"]: self.copy_to_clipboard(value, "Korisničko ime"), height=29, width=78, corner_radius=7,
                          fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 11)).pack(side="left", padx=3)
        if record.get("password"):
            ctk.CTkButton(action, text="⧉ Lozinka", command=lambda item=record: self.copy_to_clipboard(self.vault.decrypt(item["password"]), "Lozinka"), height=29, width=80, corner_radius=7,
                          fg_color=COLORS["panel_hover"], hover_color=COLORS["border"], text_color=COLORS["text"], font=("Arial", 11)).pack(side="left", padx=3)
        ctk.CTkButton(action, text="Uredi", command=lambda r=record: RecordDialog(self, r), height=29, width=60, corner_radius=7, fg_color="transparent", border_width=1, border_color=COLORS["border"], hover_color=COLORS["panel_hover"], font=("Arial", 11)).pack(side="right", padx=3)
        ctk.CTkButton(action, text="Obriši", command=lambda r=record: self.delete(r), height=29, width=64, corner_radius=7, fg_color="transparent", text_color=COLORS["danger"], hover_color="#3B1E32", font=("Arial", 11)).pack(side="right", padx=3)
        for widget in (card, head, name_label, status_label, detail_label, password_row):
            widget.bind("<Double-Button-1>", lambda _event, item=record: RecordDetailsDialog(self, item), add="+")

    def toggle_card_password(self, record: dict, value: StringVar, button: ctk.CTkButton) -> None:
        hidden = value.get().startswith("Lozinka: •")
        value.set("Lozinka: " + (self.vault.decrypt(record.get("password", "")) if hidden else "••••••••"))
        button.configure(text="◉" if hidden else "◌")

    def delete(self, record):
        if messagebox.askyesno("Obriši uslugu", f"Želite li obrisati „{record['name']}”?", parent=self):
            self.records = [item for item in self.records if item["id"] != record["id"]]
            self.vault.save(self.records)
            self.refresh()


if __name__ == "__main__":
    DigitalVault().mainloop()
