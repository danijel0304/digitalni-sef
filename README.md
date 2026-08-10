# Digitalni sef

Moderna desktop aplikacija za lokalno čuvanje podataka o pretplatama, streaming servisima, AI alatima i drugim digitalnim računima.

## Pokretanje

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

Jednostavnije: na Linuxu pokrenite `./pokreni.sh`, a na Windowsu dvaput kliknite `pokreni.bat`. Pokretači će po potrebi sami instalirati biblioteke.

Pri prvom pokretanju odaberite glavnu lozinku (najmanje 8 znakova). Ona šifrira sve spremljene lozinke, pa je nije moguće vratiti ako se zaboravi.

Podaci se čuvaju samo na računalu, u mapi `~/.digitalni_sef`. Pri prvom pokretanju nove verzije stara mapa `~/.servisni_sef` automatski se premješta u novu mapu. Aplikacija ne šalje lozinke ni druge podatke na internet.

## Privatnost izvornog koda

U repozitorij se ne spremaju podaci sefa, šifrirani privici, lokalne postavke ni sigurnosne kopije. To je osigurano datotekom `.gitignore`; prije slanja promjena ipak provjerite `git status`.

## Izdavanja

GitHub Actions provjerava svaki commit na grani `main`. Za izradu instalacijskih paketa za Windows i Linux te novog GitHub Releasea izradite i pošaljite oznaku verzije, primjerice `v1.0.0`.

Instalirana verzija aplikacije provjerava najnoviji GitHub Release pri pokretanju. U bočnoj traci možete i ručno pokrenuti provjeru; kada postoji odgovarajući Windows ili Linux paket, aplikacija ga može preuzeti, zamijeniti i ponovno pokrenuti.

Ako se glavna lozinka zaboravi, na ekranu za otključavanje postoji opcija za izradu novog sefa. To je namjerno sigurnosno rješenje: glavna lozinka se ne čuva niti šalje e-poštom, pa se postojeći šifrirani podaci ne mogu vratiti; prije brisanja sef traži dvije potvrde.

## Mogućnosti

- evidencija korisničkog imena, lozinke, prodavatelja i bilješki
- datum kupnje, istek pretplate i rok jamstva prodavatelja
- poveznice na kupnju i razgovor s prodavateljem
- pregled usluga kojima rok uskoro istječe
- cijena, valuta, učestalost naplate i automatska obnova pretplate
- mjesečni pregled troškova te filtri po kategoriji i statusu usluge
- zasebne stranice za pregled, katalog usluga i potrošnju po kategoriji
- katalog s više od 1.000 popularnih usluga, uključujući upload i dijeljenje datoteka (WeTransfer, SwissTransfer, MASV, Filemail i druge)
- brzo dodavanje iz kataloga, koje unaprijed popunjava naziv i kategoriju u obrascu
- ugrađeni uređivač kataloga za dodavanje, promjenu kategorije i uklanjanje prijedloga
- brzo stranicenje kataloga (50 stavki po stranici) i odgođena pretraga za ugodan rad s velikim katalogom
- osobni podsjetnici prije isteka pretplate, jamstva ili sljedeće naplate
- šifrirana sigurnosna kopija i vraćanje zapisa zajedno s privicima
- brzo kopiranje korisničkog imena i lozinke te zaštita od slučajnih duplikata
- šifrirani privici za račune, PDF-ove i druge dokumente
- pretraga i jednostavno uređivanje ili brisanje zapisa
- svijetla i tamna tema s pripadajućom ikonom; promjena je trenutačna i izbor se pamti
- hrvatsko i englesko sučelje koje se može promijeniti tijekom rada aplikacije
- ugrađena profesionalna ikona aplikacije i dobrovoljna PayPal donacija

## Katalog usluga

Popis ugrađenih prijedloga nalazi se u datoteci `service_catalog.py`, odvojeno od glavnog koda sučelja. U aplikaciji otvorite **Katalog usluga → Uredi katalog** za jednostavno dodavanje, promjenu ili uklanjanje stavke; lokalne izmjene spremaju se u `~/.digitalni_sef/catalog.json`. Svaku novu ugrađenu uslugu možete dodati i ručno kao stavku u `SERVICE_CATALOG` u obliku `"Naziv": "Kategorija"`.
