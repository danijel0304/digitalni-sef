"""Katalog usluga prikazan na stranici Katalog usluga i u obrascu za unos.

Svaka stavka ima naziv i kategoriju. Dodajte nove stavke ovdje; glavno sučelje
automatski preuzima kategorije i nudi ih pri brzom dodavanju.
"""

SERVICE_CATALOG = {
    # Streaming video
    "Netflix": "Streaming", "HBO Max": "Streaming", "Disney+": "Streaming", "Prime Video": "Streaming",
    "Apple TV+": "Streaming", "SkyShowtime": "Streaming", "Hulu": "Streaming", "Paramount+": "Streaming",
    "Peacock": "Streaming", "Crunchyroll": "Streaming", "MUBI": "Streaming", "DAZN": "Streaming",
    "YouTube Premium": "Streaming", "Viki": "Streaming", "Rakuten TV": "Streaming", "Plex Pass": "Streaming",
    "Nebula": "Streaming", "Curiosity Stream": "Streaming", "hayu": "Streaming", "BritBox": "Streaming",
    "Discovery+": "Streaming", "AMC+": "Streaming", "Shudder": "Streaming", "WOW": "Streaming",
    "Viaplay": "Streaming", "RTL Play Premium": "Streaming", "VOYO": "Streaming", "EON TV": "Streaming",
    "FilmBox+": "Streaming", "CineStar TV": "Streaming", "Pickbox NOW": "Streaming",
    "Apple One": "Streaming", "MagentaTV": "Streaming", "TV2 Play": "Streaming", "Molotov": "Streaming",
    # Glazba, knjige i audio
    "Spotify Premium": "Glazba i audio", "YouTube Music": "Glazba i audio", "Apple Music": "Glazba i audio",
    "Deezer": "Glazba i audio", "Tidal": "Glazba i audio", "Amazon Music": "Glazba i audio",
    "SoundCloud Go+": "Glazba i audio", "Audible": "Glazba i audio", "Storytel": "Glazba i audio",
    "BookBeat": "Glazba i audio", "Podimo": "Glazba i audio", "Scribd / Everand": "Glazba i audio",
    "Kobo Plus": "Glazba i audio", "Qobuz": "Glazba i audio", "Roon": "Glazba i audio",
    # TV, IPTV i radio
    "A1 Xplore TV": "IPTV", "Hrvatski Telekom MAXtv": "IPTV", "Telemach EON": "IPTV",
    "Iskon.TV": "IPTV", "OptiTV": "IPTV", "Total TV": "IPTV", "Moja TV": "IPTV",
    "SBB EON": "IPTV", "Viasat": "IPTV", "Xiaomi TV+": "IPTV", "Samsung TV Plus": "IPTV",
    "Tivimate Premium": "IPTV alat", "IPTV Smarters Pro": "IPTV alat", "OTT Navigator": "IPTV alat",
    "Perfect Player": "IPTV alat", "GSE Smart IPTV": "IPTV alat", "SmartOne IPTV": "IPTV alat",
    "Flix IPTV": "IPTV alat", "IBO Player": "IPTV alat", "DuplexPlay": "IPTV alat",
    # AI
    "ChatGPT Plus": "AI", "ChatGPT Pro": "AI", "Claude Pro": "AI", "Gemini": "AI",
    "Google AI Pro": "AI", "Google AI Ultra": "AI",
    "Microsoft Copilot Pro": "AI", "Perplexity Pro": "AI", "Poe": "AI", "Grok": "AI",
    "Le Chat Pro": "AI", "Meta AI": "AI", "DeepSeek": "AI", "Kimi": "AI",
    "Midjourney": "AI – slike", "DALL·E": "AI – slike", "Adobe Firefly": "AI – slike",
    "Leonardo AI": "AI – slike", "Ideogram": "AI – slike", "Canva Pro": "AI – slike",
    "Runway": "AI – video", "Pika": "AI – video", "Luma Dream Machine": "AI – video",
    "Synthesia": "AI – video", "HeyGen": "AI – video", "Descript": "AI – video",
    "ElevenLabs": "AI – zvuk", "Suno": "AI – zvuk", "Udio": "AI – zvuk",
    "Notion AI": "AI", "Grammarly Premium": "AI", "Jasper": "AI", "Writesonic": "AI",
    "QuillBot Premium": "AI", "Otter.ai": "AI", "GitHub Copilot": "AI za programiranje",
    "Cursor": "AI za programiranje", "Windsurf": "AI za programiranje", "Replit Core": "AI za programiranje",
    # Cloud i upload datoteka
    "Google One": "Cloud", "iCloud+": "Cloud", "Dropbox": "Cloud", "Dropbox Plus": "Cloud",
    "pCloud": "Cloud", "MEGA": "Cloud", "OneDrive": "Cloud", "Google Drive": "Cloud",
    "Proton Drive": "Cloud", "Sync.com": "Cloud", "Box": "Cloud", "TeraBox": "Cloud",
    "Internxt Drive": "Cloud", "Koofr": "Cloud", "Jottacloud": "Cloud", "Icedrive": "Cloud",
    "WeTransfer": "Upload datoteka", "SwissTransfer": "Upload datoteka", "Smash": "Upload datoteka",
    "TransferNow": "Upload datoteka", "Send Anywhere": "Upload datoteka", "Filemail": "Upload datoteka",
    "MASV": "Upload datoteka", "Hightail": "Upload datoteka", "Dropbox Transfer": "Upload datoteka",
    "Google Drive transfer": "Upload datoteka", "MEGA Transfer": "Upload datoteka", "MediaFire": "Upload datoteka",
    "Box Transfer": "Upload datoteka", "File.io": "Upload datoteka", "pCloud Transfer": "Upload datoteka",
    "Pixeldrain": "Upload datoteka", "SendGB": "Upload datoteka", "Wormhole": "Upload datoteka",
    "TransferXL": "Upload datoteka", "MyAirBridge": "Upload datoteka", "GoFile": "Upload datoteka",
    # Igre i zajednice
    "PlayStation Plus": "Igre", "Xbox Game Pass": "Igre", "Nintendo Switch Online": "Igre",
    "EA Play": "Igre", "Ubisoft+": "Igre", "GeForce NOW": "Igre", "Steam": "Igre",
    "Epic Games": "Igre", "Roblox Premium": "Igre", "Discord Nitro": "Igre",
    "Humble Choice": "Igre", "Final Fantasy XIV": "Igre", "World of Warcraft": "Igre",
    "Minecraft Realms": "Igre", "PlayStation Stars": "Igre",
    # Produktivnost, dizajn i razvoj
    "Microsoft 365": "Produktivnost", "Microsoft 365 Family": "Produktivnost", "Google Workspace": "Produktivnost",
    "Notion Plus": "Produktivnost", "Todoist Pro": "Produktivnost", "Trello Premium": "Produktivnost",
    "Slack Pro": "Produktivnost", "Zoom Pro": "Produktivnost", "ClickUp": "Produktivnost",
    "Miro": "Produktivnost", "Evernote": "Produktivnost", "Monday.com": "Produktivnost",
    "Adobe Creative Cloud": "Dizajn", "Figma Professional": "Dizajn", "Canva Teams": "Dizajn",
    "Affinity": "Dizajn", "Envato Elements": "Dizajn", "Freepik Premium": "Dizajn", "Sketch": "Dizajn",
    "GitHub Pro": "Razvoj", "GitLab Premium": "Razvoj", "JetBrains All Products Pack": "Razvoj",
    "Postman": "Razvoj", "Sentry": "Razvoj", "Docker": "Razvoj", "Atlassian": "Razvoj",
    # Hosting, domene i mreža
    "DigitalOcean": "Hosting", "Hetzner": "Hosting", "Vercel Pro": "Hosting", "Netlify Pro": "Hosting",
    "Cloudflare": "Hosting", "Hostinger": "Hosting", "SiteGround": "Hosting", "cPanel": "Hosting",
    "AWS": "Cloud infrastruktura", "Google Cloud": "Cloud infrastruktura", "Microsoft Azure": "Cloud infrastruktura",
    "Oracle Cloud": "Cloud infrastruktura", "OVHcloud": "Hosting", "Linode / Akamai": "Hosting",
    "Namecheap": "Domene", "GoDaddy": "Domene", "Porkbun": "Domene", "Cloudflare Registrar": "Domene",
    "Tailscale": "Mreža", "ZeroTier": "Mreža", "Ubiquiti UniFi": "Mreža",
    # Komunikacija, obrazovanje i posao
    "Proton Mail": "E-mail", "Fastmail": "E-mail",
    "Telegram Premium": "Komunikacija", "Viber Plus": "Komunikacija", "LinkedIn Premium": "Posao",
    "Canary Mail": "E-mail", "Superhuman": "E-mail", "Calendly": "Produktivnost",
    "Coursera Plus": "Obrazovanje", "Udemy": "Obrazovanje", "Skillshare": "Obrazovanje",
    "MasterClass": "Obrazovanje", "Duolingo Super": "Obrazovanje", "Brilliant": "Obrazovanje",
    "Codecademy": "Obrazovanje", "Pluralsight": "Obrazovanje", "DataCamp": "Obrazovanje",
    "Babbel": "Obrazovanje", "LinkedIn Learning": "Obrazovanje", "Rosetta Stone": "Obrazovanje",
    # Svakodnevne usluge
    "Strava": "Zdravlje i fitness", "Fitbit Premium": "Zdravlje i fitness",
    "MyFitnessPal Premium": "Zdravlje i fitness", "Nike Training Club": "Zdravlje i fitness",
    "Headspace": "Zdravlje i wellness", "Calm": "Zdravlje i wellness", "YAZIO Pro": "Zdravlje i fitness",
    "Komoot Premium": "Zdravlje i fitness", "Garmin Connect+": "Zdravlje i fitness",
    "Amazon Prime": "Kupovina", "eBay": "Kupovina", "Wolt+": "Dostava hrane",
    "Glovo Prime": "Dostava hrane", "Uber One": "Prijevoz", "Bolt Plus": "Prijevoz",
    "Revolut Premium": "Financije", "Revolut Metal": "Financije", "N26 You": "Financije",
    "Wise": "Financije", "PayPal": "Financije", "Airbnb": "Putovanja", "Booking.com": "Putovanja",
    # Sigurnost i uređaji
    "Proton Pass": "Sigurnost", "1Password": "Sigurnost", "Dashlane": "Sigurnost", "Keeper": "Sigurnost",
    "Bitdefender": "Sigurnost", "ESET": "Sigurnost", "Kaspersky": "Sigurnost", "Malwarebytes": "Sigurnost",
    "NordVPN": "VPN", "Surfshark": "VPN", "ExpressVPN": "VPN", "Proton VPN": "VPN",
    "Mullvad VPN": "VPN", "CyberGhost VPN": "VPN", "Private Internet Access": "VPN",
    "Synology C2": "Cloud", "Ring Protect": "Pametni dom", "Google Nest Aware": "Pametni dom",
    "AppleCare+": "Jamstvo uređaja", "Samsung Care+": "Jamstvo uređaja", "Xiaomi Care": "Jamstvo uređaja",
    # Fotografija, video i kreativni sadržaj
    "Adobe Lightroom": "Fotografija", "Adobe Photoshop": "Fotografija", "Capture One": "Fotografija",
    "DxO PhotoLab": "Fotografija", "Topaz Photo AI": "Fotografija", "Luminar Neo": "Fotografija",
    "VSCO": "Fotografija", "500px": "Fotografija", "Flickr Pro": "Fotografija",
    "Shutterstock": "Stock sadržaj", "Adobe Stock": "Stock sadržaj", "iStock": "Stock sadržaj",
    "Getty Images": "Stock sadržaj", "Artlist": "Stock sadržaj", "Epidemic Sound": "Stock sadržaj",
    "Motion Array": "Stock sadržaj", "Storyblocks": "Stock sadržaj", "MotionElements": "Stock sadržaj",
    "Vimeo": "Video", "Vimeo OTT": "Video", "Frame.io": "Video", "Wistia": "Video",
    "VEED": "Video", "Kapwing": "Video", "Filmora": "Video", "DaVinci Resolve Studio": "Video",
    # Društvene mreže, web i objavljivanje
    "X Premium": "Društvene mreže", "Facebook Meta Verified": "Društvene mreže",
    "Instagram Meta Verified": "Društvene mreže", "Snapchat+": "Društvene mreže",
    "TikTok": "Društvene mreže", "Reddit Premium": "Društvene mreže", "Pinterest Business": "Društvene mreže",
    "YouTube Premium Family": "Društvene mreže", "Patreon": "Kreatori", "Ko-fi": "Kreatori",
    "Substack": "Kreatori", "OnlyFans": "Kreatori", "Twitch Turbo": "Streaming",
    "WordPress.com": "Web stranice", "Wix": "Web stranice", "Squarespace": "Web stranice",
    "Webflow": "Web stranice", "Framer": "Web stranice", "Carrd": "Web stranice",
    "Shopify": "E-trgovina", "WooCommerce": "E-trgovina", "Etsy Plus": "E-trgovina",
    "Sellfy": "E-trgovina", "Gumroad": "E-trgovina", "Printful": "E-trgovina",
    # Plaćanja, računovodstvo i poslovanje
    "Payoneer": "Financije", "Monese": "Financije", "Curve": "Financije",
    "Trade Republic": "Financije", "eToro": "Financije", "Trading 212": "Financije",
    "Coinbase One": "Kripto", "Kraken": "Kripto", "Binance": "Kripto", "Ledger Recover": "Kripto",
    "Wise Business": "Financije", "Stripe": "Poslovanje", "SumUp": "Poslovanje",
    "QuickBooks": "Računovodstvo", "Xero": "Računovodstvo", "FreshBooks": "Računovodstvo",
    "Invoice Ninja": "Računovodstvo", "Zoho One": "Poslovanje", "HubSpot": "Poslovanje",
    "Salesforce": "Poslovanje", "Pipedrive": "Poslovanje", "Zendesk": "Korisnička podrška",
    "Intercom": "Korisnička podrška", "Freshdesk": "Korisnička podrška",
    # Mobilne, internetske i lokalne usluge
    "A1 Hrvatska": "Mobilne usluge", "Hrvatski Telekom": "Mobilne usluge", "Telemach Hrvatska": "Mobilne usluge",
    "bonbon": "Mobilne usluge", "Iskon Internet": "Internet", "Optima Telekom": "Internet",
    "Starlink": "Internet", "T-Mobile": "Mobilne usluge", "Vodafone": "Mobilne usluge",
    "Google Fi": "Mobilne usluge", "Airalo": "eSIM", "Nomad eSIM": "eSIM", "Holafly": "eSIM",
    "Google Maps": "Navigacija", "TomTom GO": "Navigacija", "Sygic": "Navigacija",
    "Park4Night": "Putovanja", "FlixBus": "Putovanja", "Omio": "Putovanja",
    "Eurowings": "Putovanja", "Ryanair": "Putovanja", "Priority Pass": "Putovanja",
    # Auto, dom i obitelj
    "Tesla Premium Connectivity": "Auto", "BMW ConnectedDrive": "Auto", "Mercedes me": "Auto",
    "Porsche Connect": "Auto", "Toyota Connected": "Auto", "Škoda Connect": "Auto",
    "Home Assistant Cloud": "Pametni dom", "Philips Hue": "Pametni dom", "TP-Link Tapo Care": "Pametni dom",
    "Arlo Secure": "Pametni dom", "Eufy Security": "Pametni dom", "Alexa": "Pametni dom",
    "Google One Family": "Cloud", "Apple One Family": "Streaming", "Life360": "Obitelj",
    "Microsoft Family Safety": "Obitelj", "Google Family Link": "Obitelj",
    # Još razvojnih i tehničkih alata
    "GitHub Team": "Razvoj", "GitHub Enterprise": "Razvoj", "Bitbucket": "Razvoj",
    "Azure DevOps": "Razvoj", "Linear": "Razvoj", "Jira": "Razvoj", "Confluence": "Razvoj",
    "Supabase": "Razvoj", "Firebase": "Razvoj", "MongoDB Atlas": "Razvoj",
    "PlanetScale": "Razvoj", "Neon": "Razvoj", "Render": "Hosting", "Railway": "Hosting",
    "Fly.io": "Hosting", "Koyeb": "Hosting", "GitHub Pages": "Hosting",
    "Statuspage": "Razvoj", "UptimeRobot": "Nadzor", "Better Uptime": "Nadzor",
    "Datadog": "Nadzor", "New Relic": "Nadzor", "Grafana Cloud": "Nadzor",
    # Čitanje, vijesti i specijalizirani sadržaj
    "Readly": "Časopisi", "PressReader": "Časopisi", "The New York Times": "Vijesti",
    "The Economist": "Vijesti", "Financial Times": "Vijesti", "The Athletic": "Vijesti",
    "Medium": "Čitanje", "Blinkist": "Čitanje", "Readwise": "Čitanje", "Pocket Premium": "Čitanje",
    "Ancestry": "Obitelj", "MyHeritage": "Obitelj", "Chess.com": "Hobiji",
    "Yousician": "Hobiji", "Simply Piano": "Hobiji", "Adobe Acrobat": "Produktivnost",
    # Dodatni AI alati i istraživanje
    "Google AI Plus": "AI", "NotebookLM": "AI", "Google Flow": "AI – video",
    "Microsoft 365 Copilot": "AI", "Microsoft Copilot": "AI", "Amazon Q": "AI za programiranje",
    "Tabnine": "AI za programiranje", "Codeium": "AI za programiranje", "Sourcegraph Cody": "AI za programiranje",
    "Amazon Bedrock": "AI infrastruktura", "OpenRouter": "AI infrastruktura", "Replicate": "AI infrastruktura",
    "Hugging Face": "AI infrastruktura", "Civitai": "AI – slike", "Krea": "AI – slike",
    "Kaiber": "AI – video", "D-ID": "AI – video", "Murf AI": "AI – zvuk",
    "Speechify": "AI – zvuk", "DeepL Pro": "AI", "Lingvanex": "AI",
    # Apple, Android i softver
    "Apple Developer Program": "Razvoj", "Google Play Console": "Razvoj", "Microsoft 365 Personal": "Produktivnost",
    "Final Cut Pro": "Video", "Logic Pro": "Glazba i audio", "Setapp": "Softver",
    "CleanMyMac X": "Softver", "Parallels Desktop": "Softver", "VMware Fusion": "Softver",
    "Windows 365": "Cloud infrastruktura", "Microsoft PC Game Pass": "Igre", "Xbox Cloud Gaming": "Igre",
    "Samsung Galaxy Store": "Mobilne usluge", "Google Play Pass": "Mobilne usluge",
    # Sigurnosno kopiranje, privatnost i podrška
    "Backblaze": "Sigurnosna kopija", "IDrive": "Sigurnosna kopija", "Acronis Cyber Protect": "Sigurnosna kopija",
    "Carbonite": "Sigurnosna kopija", "EaseUS Todo Backup": "Sigurnosna kopija", "Veeam": "Sigurnosna kopija",
    "Proton Mail Plus": "E-mail", "Tuta Mail": "E-mail", "StartMail": "E-mail",
    "SimpleLogin": "Privatnost", "Addy.io": "Privatnost", "Incogni": "Privatnost",
    "DeleteMe": "Privatnost", "Aura": "Sigurnost", "Identity Guard": "Sigurnost",
    "TeamViewer": "Daljinski pristup", "AnyDesk": "Daljinski pristup", "Splashtop": "Daljinski pristup",
    # Prehrana, sport, kulturni sadržaj i ulaznice
    "Peloton": "Zdravlje i fitness", "Freeletics": "Zdravlje i fitness", "Centr": "Zdravlje i fitness",
    "Zwift": "Zdravlje i fitness", "AllTrails+": "Zdravlje i fitness", "BetterHelp": "Zdravlje i wellness",
    "Noom": "Zdravlje i wellness", "Tinder Gold": "Društvene mreže", "Bumble Premium": "Društvene mreže",
    "Too Good To Go": "Dostava hrane", "Just Eat Plus": "Dostava hrane", "Deliveroo Plus": "Dostava hrane",
    "Tripadvisor Plus": "Putovanja", "TripIt Pro": "Putovanja", "LoungeKey": "Putovanja",
    "GetYourGuide": "Putovanja", "Klook": "Putovanja", "Ticketmaster": "Ulaznice",
    "Eventim": "Ulaznice", "CineStar": "Ulaznice", "Deezer Family": "Glazba i audio",
    # Znanje, znanost i profesionalni alati
    "Wolfram|Alpha Pro": "Obrazovanje", "O'Reilly Learning": "Obrazovanje", "edX": "Obrazovanje",
    "Khan Academy": "Obrazovanje", "The Great Courses Plus": "Obrazovanje", "Curio": "Čitanje",
    "JSTOR": "Istraživanje", "Statista": "Istraživanje", "Mendeley": "Istraživanje",
    "ResearchGate": "Istraživanje", "Scribbr": "Obrazovanje", "Overleaf": "Obrazovanje",
    "Autodesk": "Profesionalni alati", "AutoCAD": "Profesionalni alati", "SketchUp": "Profesionalni alati",
    "SolidWorks": "Profesionalni alati", "ArcGIS": "Profesionalni alati", "Bluebeam": "Profesionalni alati",
    # Marketing, analitika i automatizacija
    "Mailchimp": "Marketing", "Brevo": "Marketing", "ConvertKit": "Marketing",
    "Buffer": "Marketing", "Hootsuite": "Marketing", "Later": "Marketing", "Metricool": "Marketing",
    "Google Analytics": "Analitika", "Plausible": "Analitika", "Matomo": "Analitika",
    "Hotjar": "Analitika", "Mixpanel": "Analitika", "Amplitude": "Analitika",
    "Zapier": "Automatizacija", "Make": "Automatizacija", "n8n": "Automatizacija",
    "IFTTT Pro": "Automatizacija", "Pabbly Connect": "Automatizacija", "Bardeen": "Automatizacija",
}

# Širi popis je odvojen od osnovnog rječnika da je nadopunjavanje pregledno.
# setdefault čuva ručno razvrstane stavke iz glavnog kataloga ako se naziv ponovi.
EXPANDED_SERVICES = {
    "Streaming": """Tubi Pluto TV The Roku Channel Freevee Kanopy Acorn TV Aha ZEE5 Hoichoi iQIYI Viu Rakuten Viki Youku Tencent Video Bilibili TVer U-NEXT Abema TV5MONDEplus ARTE.tv Plex Crackle Fandor Revry Dekkoo OUTtv Topic MHz Choice Kocowa AsianCrush FilmRise Xumo Play DistroTV Local Now Redbox Live TV Filmzie""".split("|"),
    "Streaming uživo": """Sling TV Fubo Philo DirecTV Stream YouTube TV Hulu + Live TV ESPN+ ESPN Unlimited Fanatiz FloSports B/R Sports NBA League Pass NFL+ MLB.TV NHL.TV UFC Fight Pass Formula 1 TV MotoGP Video Tennis TV WTA TV EuroLeague TV GCN+ WWE Network TrillerTV DAZN Boxing NOW TV Sports beIN CONNECT Viaplay Sports Stan Sport Kayo Sports Optus Sport""".split("|"),
    "Glazba i audio": """Pandora Napster iHeartRadio TuneIn Mixcloud Bandcamp Nugs.net Qello Concerts Idagio Primephonic Radio Paradise Radio Garden AccuRadio JioSaavn Gaana Anghami Boomplay Audiomack Audiobooks.com Libro.fm Chirp Blinkist Audio Pocket Casts Plus Overcast Castro Downcast Podbean Acast Plus Wondery+ Luminary The Athletic Audio""".split("|"),
    "Igre": """Amazon Luna Boosteroid Shadow PC Blacknut Antstream Arcade Apple Arcade Google Play Games Pass Utomik Blacknut Xbox Game Pass Ultimate PlayStation Plus Essential PlayStation Plus Extra PlayStation Plus Premium Nintendo Switch Online Expansion Pack EA Play Pro Ubisoft+ Classics Ubisoft+ Premium Battle.net World of Warships World of Tanks War Thunder Old School RuneScape RuneScape Membership EVE Online The Elder Scrolls Online Fallout 76 GTA+ Roblox Premium 450 Roblox Premium 1000 Roblox Premium 2200 Discord Nitro Basic Discord Nitro Classic Fortnite Crew Minecraft Realms Plus Pokémon HOME Premium Hearthstone Battlegrounds Season Pass""".split("|"),
    "Cloud": """Filen Tresorit SpiderOak ONE NordLocker Degoo Yandex Disk IDrive e2 Wasabi Backblaze B2 Storj S3Drive OpenDrive Zoolz ElephantDrive LuckyCloud Nextcloud Hub ownCloud Seafile Filebase CloudMounter Mountain Duck Cryptomator Boxcryptor Enpass Cloud CrossClave FileRun Resilio Sync GoodSync Air Explorer MultCloud CloudHQ Otixo Rclone Proton Docs Zoho WorkDrive Egnyte Citrix ShareFile""".split("|"),
    "Produktivnost": """Asana Wrike Basecamp MeisterTask TickTick Things 3 Sunsama Akiflow Routine Motion Reclaim Clockwise Fantastical BusyCal MindNode XMind Obsidian Sync Obsidian Publish Craft NotePlan Standard Notes Joplin Cloud Simplenote Bear App Ulysses Scrivener LanguageTool Pro WPS Office OnlyOffice Zoho Workplace LibreOffice Enterprise Quip Coda Airtable Smartsheet Fibery Nuclino Slite Height""".split("|"),
    "Komunikacija": """Microsoft Teams Google Meet Cisco Webex GoTo Meeting Whereby Jitsi Meet RingCentral 8x8 Dialpad OpenPhone Aircall Grasshopper Nextiva Vonage Business CloudTalk Front Zoom Workplace Loom Vidyard Tella Riverside StreamYard Restream Discord Server Boost Guilded Mumble TeamSpeak Element Wire Threema Signal Telegram Business WhatsApp Business LINE KakaoTalk WeChat""".split("|"),
    "Razvoj": """Gitpod Codespaces CodeSandbox StackBlitz CodePen JSFiddle Glitch Glitch Pro CodeCanyon Packagist npm Pro Maven Central JFrog Artifactory Sonatype Nexus CircleCI Travis CI Buildkite TeamCity Jenkins Cloud Semaphore CI Buddy GitKraken Tower Fork Sourcetree Sublime Text JetBrains Space CodeClimate Codacy SonarCloud Snyk Mend Renovate Dependabot LaunchDarkly Flagsmith PostHog LogRocket""".split("|"),
    "Hosting": """DreamHost Bluehost IONOS A2 Hosting GreenGeeks WP Engine Kinsta Flywheel Pressable Pantheon Platform.sh Heroku Replit Deploy Cloudways Vultr Scaleway Contabo Exoscale UpCloud Bunny.net Fastly KeyCDN StackPath Imperva Vercel Enterprise Netlify Enterprise Surge.sh Neocities AwardSpace InfinityFree GitLab Pages Firebase Hosting Amazon Lightsail Google App Engine Azure App Service Cloudflare Pages""".split("|"),
    "Domene": """Gandi Dynadot Hover OVH Domains IONOS Domains Network Solutions Register.com Domain.com Name.com EuroDNS INWX MarkMonitor Sedo Afternic DAN.com Namesilo Spaceship Porkbun Domains Tucows OpenSRS Cloudns DNS Made Easy NS1 Hurricane Electric DNS ClouDNS PowerDNS No-IP Dynu Duck DNS FreeDNS""".split("|"),
    "Sigurnost": """Bitwarden Premium Bitwarden Families RoboForm LastPass Proton Sentinel YubiKey Bio TOTP Authy 2FAS Aegis Authenticator Microsoft Authenticator Google Authenticator Okta Verify Duo Mobile JumpCloud OneLogin Ping Identity Auth0 Stytch Huntress SentinelOne CrowdStrike Falcon Sophos Home Avast Premium AVG Ultimate F-Secure Total Avira Prime Webroot McAfee+ Norton 360 G DATA Panda Dome ZoneAlarm GlassWire""".split("|"),
    "VPN": """IVPN Windscribe PrivateVPN VyprVPN PureVPN StrongVPN Hide.me VPN Unlimited Hotspot Shield TunnelBear Atlas VPN PrivadoVPN hide.me Proton VPN Plus NordLayer Perimeter 81 Cloudflare WARP Outline VPN Amnezia VPN AirVPN OVPN AzireVPN Perfect Privacy TorGuard VPN.ac HMA VPN Goose VPN ZoogVPN Urban VPN AdGuard VPN Mozilla VPN FastestVPN""".split("|"),
    "AI": """Google AI Plus Microsoft Copilot Microsoft Copilot Pro SuperGrok xAI API GroqCloud Together AI Fireworks AI Anyscale Modal AI Banana.dev Scale AI Labelbox Humanloop LangSmith Langfuse Weights & Biases Comet ML Galileo AI Vellum Dust AI Dust.tt Flowise Langflow Dify Voiceflow Botpress Tidio AI Intercom Fin Forethought Ada CX Decagon Sierra AI Lindy AI Zapier Agents Lindy Relevance AI""".split("|"),
    "AI – slike": """Stable Diffusion DreamStudio NightCafe Dream by WOMBO NightCafe Pro Playground AI Mage Space NightCafe Studio Kittl AI Artbreeder Artflow Picsart Gold PhotoRoom Pro Remini Pro Pixelcut Pro Fotor Pro BeFunky Plus VanceAI Clipdrop Pro Flair AI Pebblely Mokker AI ProductScope AI Magnific AI Upscayl Pro LetzAI Dzine AI Tensor.Art SeaArt AI PixAI Meitu AI""".split("|"),
    "AI – video": """OpenAI Sora Veo Kling AI Hailuo AI PixVerse AI Vidu AI Haiper AI Genmo AI Pollo AI Captions AI OpusClip Vizard AI Wisecut AI InVideo AI FlexClip AI Pictory AI Fliki AI Steve AI Colossyan Elai.io Hour One Tavus Synthesys Reface Unboring HeyGen Avatar Akool AI Dreamina AI Hedra AI Viggle AI Hyperhuman AI""".split("|"),
    "Dizajn": """Penpot Lunacy CorelDRAW Corel Vector VistaCreate PicMonkey Snappa Easil Creatopy Design Pickle RelayThat Visme Genially Prezi Pitch Beautiful.ai Tome Gamma App Mural Whimsical FigJam Overflow ProtoPie Principle Origami Studio Zeplin Avocode Marvel App Balsamiq UXPin MockFlow Framer Sites Dorik Typedream Unicorn Platform""".split("|"),
    "Marketing": """Semrush Ahrefs Moz Pro Ubersuggest Mangools Serpstat SE Ranking SpyFu Similarweb BuzzSumo SparkToro Brandwatch Mention Awario Brand24 Talkwalker Sprout Social SocialBee Planable Publer Sendible Agorapulse CoSchedule Tailwind SocialPilot Iconosquare Loomly NapoleonCat Drip ActiveCampaign Klaviyo Campaign Monitor GetResponse AWeber MailerLite""".split("|"),
    "E-trgovina": """BigCommerce Magento Adobe Commerce PrestaShop OpenCart Ecwid Shopware Squarespace Commerce Wix Stores Shift4Shop Volusion 3dcart SellNow Payhip Podia Teachable Thinkific Kajabi LearnWorlds Memberful Patreon Pro Ko-fi Gold Buy Me a Coffee Fourthwall Spring Redbubble Society6 Zazzle Spreadshirt Gelato Printify Gooten Teespring""".split("|"),
    "Financije": """Monzo Starling Bank Chase UK bunq Wise Business Paysera Skrill Neteller Payoneer Revolut Business N26 Metal Curve Black Curve Metal Trade Republic Scalable Capital DEGIRO Interactive Brokers Robinhood Webull M1 Finance Acorns Betterment Wealthfront Mint Monarch Money YNAB PocketGuard Emma Wallet Plum Moneybox Finary Delta Investment Tracker Sharesight""".split("|"),
    "Kripto": """Crypto.com Gemini Exchange Bitstamp Bitpanda KuCoin OKX Bybit Gate.io MEXC CoinEx Uphold Nexo Celsius Wallet Exodus Trezor Suite Ledger Live Trust Wallet MetaMask Rabby Wallet Phantom Wallet Coinbase Wallet Rainbow Wallet Safe Wallet CoinStats CoinMarketCap CoinGecko Koinly CoinTracker CoinLedger TaxBit BlockFi Wallet Fold App""".split("|"),
    "Obrazovanje": """Udacity FutureLearn OpenClassrooms Treehouse Frontend Masters Egghead.io Scrimba Exercism LeetCode Premium HackerRank Codewars Interview Cake Educative A Cloud Guru Cloud Academy Linux Academy Brilliant.org Memrise Busuu Mondly Drops Language Mango Languages Preply italki Cambly Outschool Domestika CreativeLive Craftsy The Open University MIT OpenCourseWare OpenSesame""".split("|"),
    "Zdravlje i fitness": """Les Mills+ Alo Moves FitOn Pro Daily Burn Beachbody on Demand Tone It Up Centr Fitbod Strong App Hevy Premium JEFIT Strava Summit TrainingPeaks Premium Final Surge Wahoo SYSTM Rouvy TrainerRoad Nike Run Club Premium Adidas Running Premium MapMyRun Premium Runkeeper Go Premium Sweat Kayla Fitness+ EvolveYou Fiit App Glo Yoga Down Dog Premium Insight Timer""".split("|"),
    "Putovanja": """Hopper Skyscanner Plus Kiwi.com Opodo eDreams Lastminute.com TravelPerk Navan Travelport Expedia One Key Hotels.com One Key Vrbo One Key Marriott Bonvoy Hilton Honors IHG One Rewards Accor ALL Radisson Rewards Wyndham Rewards World of Hyatt Air France Flying Blue Lufthansa Miles & More British Airways Executive Club KLM Flying Blue Rail Europe Trainline Omio Plus Rome2Rio Booking Genius""".split("|"),
    "Mobilne usluge": """Lycamobile Lebara giffgaff Mint Mobile Visible Google Fi Vodafone VOXI EE O2 UK Three UK Orange SFR Bouygues Telecom Free Mobile TIM Italia Vodafone Italia Iliad Italy Telekom Deutschland Congstar ALDI TALK simyo Blau Tello US Mobile Cricket Wireless Metro by T-Mobile Boost Mobile Straight Talk Tracfone Verizon AT&T Prepaid T-Mobile Prepaid""".split("|"),
    "Pametni dom": """SmartThings SmartThings Find Aqara Home Homey Pro Home Assistant Cloud Smart Life Tuya eWeLink Sonoff SwitchBot Kasa Smart Meross Nanoleaf Govee Wyze Cam Plus Reolink Cloud Blink Subscription Nest Aware Plus Ecobee Smart Security Yale Access August Home Schlage Home Bosch Smart Home Somfy TaHoma IKEA Home smart Dyson Link Roborock Qrevo Dreamehome""".split("|"),
    "Auto": """OnStar FordPass FordPass Connect myChevrolet myGMC myCadillac Hyundai Bluelink Kia Connect Genesis Connected Services NissanConnect INFINITI InTouch Mazda Connected Services HondaLink AcuraLink Subaru STARLINK Lexus Enform myAudi Audi connect Volvo Cars app Volkswagen We Connect MINI Connected Jeep Connect Ram Connect Fiat Uconnect Peugeot Services Citroën Services Renault Connect Dacia Media Control""".split("|"),
    "Nadzor": """Pingdom Site24x7 StatusCake HetrixTools Freshping Hyperping Checkly Cronitor Better Stack PagerDuty Opsgenie VictorOps xMatters Incident.io Rootly FireHydrant Atlassian Statuspage Instatus Cachet Uptime Kuma Cabot Healthchecks.io Dead Man's Snitch Sentry.io Rollbar Bugsnag Honeybadger Raygun AppSignal Elastic Observability Splunk Observability Dynatrace""".split("|"),
}

for category, names in EXPANDED_SERVICES.items():
    for name in names:
        normalized = name.strip()
        if normalized:
            SERVICE_CATALOG.setdefault(normalized, category)

# Gornji blok služi kao pregled izvora skupina; ove stavke ga zamjenjuju
# pojedinačnim nazivima kako bi se naziv poput "Pluto TV" vodio kao jedna usluga.
for _names in EXPANDED_SERVICES.values():
    for _name in _names:
        SERVICE_CATALOG.pop(_name.strip(), None)

GLOBAL_SERVICE_EXPANSION = {
    "Streaming": "Tubi|Pluto TV|The Roku Channel|Amazon Freevee|Kanopy|Acorn TV|Aha|ZEE5|Hoichoi|iQIYI|Viu|Youku|Tencent Video|Bilibili|TVer|U-NEXT|Abema|TV5MONDEplus|ARTE.tv|Crackle|Fandor|Revry|Dekkoo|OUTtv|Topic|MHz Choice|Kocowa|AsianCrush|FilmRise|Xumo Play|DistroTV|Local Now|Redbox Live TV|Filmzie|Howdy".split("|"),
    "Streaming uživo": "Sling TV|Fubo|Philo|DirecTV Stream|YouTube TV|Hulu + Live TV|ESPN+|ESPN Unlimited|Fanatiz|FloSports|B/R Sports|NBA League Pass|NFL+|MLB.TV|NHL.TV|UFC Fight Pass|Formula 1 TV|MotoGP Video|Tennis TV|WTA TV|EuroLeague TV|GCN+|WWE Network|TrillerTV|DAZN Boxing|NOW TV Sports|beIN CONNECT|Viaplay Sports|Stan Sport|Kayo Sports|Optus Sport".split("|"),
    "Glazba i audio": "Pandora|Napster|iHeartRadio|TuneIn|Mixcloud|Bandcamp|Nugs.net|Qello Concerts|Idagio|Radio Paradise|Radio Garden|AccuRadio|JioSaavn|Gaana|Anghami|Boomplay|Audiomack|Audiobooks.com|Libro.fm|Chirp|Blinkist Audio|Pocket Casts Plus|Overcast|Castro|Downcast|Podbean|Acast Plus|Wondery+|Luminary|Radio France Premium|BBC Sounds|SiriusXM|SoundHound|Audiomack+|Qobuz Sublime".split("|"),
    "Igre": "Amazon Luna|Boosteroid|Shadow PC|Blacknut|Antstream Arcade|Utomik|Apple Arcade|Google Play Pass|Xbox Game Pass Ultimate|PlayStation Plus Essential|PlayStation Plus Extra|PlayStation Plus Premium|Nintendo Switch Online Expansion Pack|EA Play Pro|Ubisoft+ Classics|Ubisoft+ Premium|Battle.net|World of Warships|World of Tanks|War Thunder|Old School RuneScape|RuneScape Membership|EVE Online|The Elder Scrolls Online|Fallout 76|GTA+|Roblox Premium 450|Roblox Premium 1000|Roblox Premium 2200|Discord Nitro Basic|Fortnite Crew|Minecraft Realms Plus|Pokémon HOME Premium|Hearthstone Battlegrounds Season Pass|Final Fantasy XI".split("|"),
    "Cloud": "Filen|Tresorit|SpiderOak ONE|NordLocker|Degoo|Yandex Disk|IDrive e2|Wasabi|Backblaze B2|Storj|S3Drive|OpenDrive|Zoolz|ElephantDrive|LuckyCloud|Nextcloud Hub|ownCloud|Seafile|Filebase|CloudMounter|Mountain Duck|Cryptomator|Boxcryptor|Enpass Cloud|CrossClave|FileRun|Resilio Sync|GoodSync|Air Explorer|MultCloud|CloudHQ|Otixo|Rclone|Zoho WorkDrive|Egnyte".split("|"),
    "Produktivnost": "Asana|Wrike|Basecamp|MeisterTask|TickTick|Things 3|Sunsama|Akiflow|Routine|Motion|Reclaim|Clockwise|Fantastical|BusyCal|MindNode|XMind|Obsidian Sync|Obsidian Publish|Craft|NotePlan|Standard Notes|Joplin Cloud|Simplenote|Bear App|Ulysses|Scrivener|LanguageTool Pro|WPS Office|OnlyOffice|Zoho Workplace|Quip|Coda|Airtable|Smartsheet|Fibery".split("|"),
    "Komunikacija": "Microsoft Teams|Google Meet|Cisco Webex|GoTo Meeting|Whereby|Jitsi Meet|RingCentral|8x8|Dialpad|OpenPhone|Aircall|Grasshopper|Nextiva|Vonage Business|CloudTalk|Front|Zoom Workplace|Loom|Vidyard|Tella|Riverside|StreamYard|Restream|Guilded|Mumble|TeamSpeak|Element|Wire|Threema|Signal|Telegram Business|WhatsApp Business|LINE|KakaoTalk|WeChat".split("|"),
    "Razvoj": "Gitpod|GitHub Codespaces|CodeSandbox|StackBlitz|CodePen|JSFiddle|Glitch|CodeCanyon|Packagist|npm Pro|JFrog Artifactory|Sonatype Nexus|CircleCI|Travis CI|Buildkite|TeamCity|Jenkins Cloud|Semaphore CI|Buddy|GitKraken|Tower|Fork|SourceTree|Sublime Text|JetBrains Space|CodeClimate|Codacy|SonarCloud|Snyk|Mend|Renovate|LaunchDarkly|Flagsmith|PostHog|LogRocket".split("|"),
    "Hosting": "DreamHost|Bluehost|IONOS|A2 Hosting|GreenGeeks|WP Engine|Kinsta|Flywheel|Pressable|Pantheon|Platform.sh|Heroku|Cloudways|Vultr|Scaleway|Contabo|Exoscale|UpCloud|Bunny.net|Fastly|KeyCDN|StackPath|Imperva|Surge.sh|Neocities|AwardSpace|InfinityFree|GitLab Pages|Firebase Hosting|Amazon Lightsail|Google App Engine|Azure App Service|Cloudflare Pages|Render|Railway".split("|"),
    "Domene": "Gandi|Dynadot|Hover|OVH Domains|Network Solutions|Register.com|Domain.com|Name.com|EuroDNS|INWX|MarkMonitor|Sedo|Afternic|DAN.com|NameSilo|Spaceship|Tucows|OpenSRS|Cloudns|DNS Made Easy|NS1|Hurricane Electric DNS|ClouDNS|PowerDNS|No-IP|Dynu|Duck DNS|FreeDNS|Google Domains|DreamHost Domains|Porkbun Domains|IONOS Domains|Gandi Corporate|AWS Route 53|Google Cloud DNS".split("|"),
    "Sigurnost": "Bitwarden Premium|Bitwarden Families|RoboForm|LastPass|YubiKey Bio|Authy|2FAS|Aegis Authenticator|Microsoft Authenticator|Google Authenticator|Okta Verify|Duo Mobile|JumpCloud|OneLogin|Ping Identity|Auth0|Stytch|Huntress|SentinelOne|CrowdStrike Falcon|Sophos Home|Avast Premium|AVG Ultimate|F-Secure Total|Avira Prime|Webroot|McAfee+|Norton 360|G DATA|Panda Dome|ZoneAlarm|GlassWire|Malwarebytes Premium|ESET Home Security|Kaspersky Plus".split("|"),
    "VPN": "IVPN|Windscribe|PrivateVPN|VyprVPN|PureVPN|StrongVPN|hide.me|VPN Unlimited|Hotspot Shield|TunnelBear|PrivadoVPN|NordLayer|Perimeter 81|Cloudflare WARP|Outline VPN|Amnezia VPN|AirVPN|OVPN|AzireVPN|Perfect Privacy|TorGuard|VPN.ac|HMA VPN|Goose VPN|ZoogVPN|Urban VPN|AdGuard VPN|Mozilla VPN|FastestVPN|IPVanish|Private Internet Access|Hola VPN|Touch VPN|ZenMate VPN|ClearVPN".split("|"),
    "AI": "Google AI Plus|SuperGrok|xAI API|GroqCloud|Together AI|Fireworks AI|Anyscale|Modal|Banana.dev|Scale AI|Labelbox|Humanloop|LangSmith|Langfuse|Weights & Biases|Comet ML|Galileo AI|Vellum|Dust|Flowise|Langflow|Dify|Voiceflow|Botpress|Tidio AI|Intercom Fin|Forethought|Ada CX|Decagon|Sierra AI|Lindy AI|Relevance AI|CrewAI|AutoGen|Pydantic AI".split("|"),
    "AI – slike": "DreamStudio|NightCafe|Dream by WOMBO|Playground AI|Mage Space|Kittl AI|Artbreeder|Artflow|Picsart Gold|PhotoRoom Pro|Remini Pro|Pixelcut Pro|Fotor Pro|BeFunky Plus|VanceAI|Clipdrop Pro|Flair AI|Pebblely|Mokker AI|ProductScope AI|Magnific AI|LetzAI|Dzine AI|Tensor.Art|SeaArt AI|PixAI|Meitu AI|Imagine AI|Photoleap|Prisma|Lensa|DeepAI|StarryAI|Canva Magic Studio|PicWish".split("|"),
    "AI – video": "OpenAI Sora|Google Veo|Kling AI|Hailuo AI|PixVerse AI|Vidu AI|Haiper AI|Genmo AI|Pollo AI|Captions AI|OpusClip|Vizard AI|Wisecut|InVideo AI|FlexClip AI|Pictory|Fliki|Steve AI|Colossyan|Elai.io|Hour One|Tavus|Synthesys|Akool|Dreamina|Hedra AI|Viggle AI|Hyperhuman|Luma AI|VEED AI|CapCut Pro|Filmora AI|Descript AI|Runway Gen-4|Pika 2.0".split("|"),
    "Dizajn": "Penpot|Lunacy|CorelDRAW|Corel Vector|VistaCreate|PicMonkey|Snappa|Easil|Creatopy|Design Pickle|RelayThat|Visme|Genially|Prezi|Pitch|Beautiful.ai|Tome|Gamma|Mural|Whimsical|FigJam|Overflow|ProtoPie|Principle|Origami Studio|Zeplin|Avocode|Marvel App|Balsamiq|UXPin|MockFlow|Dorik|Typedream|Unicorn Platform|Siter.io".split("|"),
    "Marketing": "Semrush|Ahrefs|Moz Pro|Ubersuggest|Mangools|Serpstat|SE Ranking|SpyFu|Similarweb|BuzzSumo|SparkToro|Brandwatch|Mention|Awario|Brand24|Talkwalker|Sprout Social|SocialBee|Planable|Publer|Sendible|Agorapulse|CoSchedule|Tailwind|SocialPilot|Iconosquare|Loomly|NapoleonCat|Drip|ActiveCampaign|Klaviyo|Campaign Monitor|GetResponse|AWeber|MailerLite".split("|"),
    "E-trgovina": "BigCommerce|Magento|Adobe Commerce|PrestaShop|OpenCart|Ecwid|Shopware|Squarespace Commerce|Wix Stores|Shift4Shop|Volusion|Payhip|Podia|Teachable|Thinkific|Kajabi|LearnWorlds|Memberful|Patreon Pro|Ko-fi Gold|Buy Me a Coffee|Fourthwall|Spring|Redbubble|Society6|Zazzle|Spreadshirt|Gelato|Printify|Gooten|Teespring|Faire|Faire Direct|Etsy Plus|Amazon Seller Central".split("|"),
    "Financije": "Monzo|Starling Bank|Chase UK|bunq|Wise Business|Paysera|Skrill|Neteller|Revolut Business|N26 Metal|Curve Black|Curve Metal|Trade Republic|Scalable Capital|DEGIRO|Interactive Brokers|Robinhood|Webull|M1 Finance|Acorns|Betterment|Wealthfront|Monarch Money|YNAB|PocketGuard|Emma Wallet|Plum|Moneybox|Finary|Delta Investment Tracker|Sharesight|Personal Capital|Tiller Money|Goodbudget|Spendee".split("|"),
    "Kripto": "Crypto.com|Gemini Exchange|Bitstamp|Bitpanda|KuCoin|OKX|Bybit|Gate.io|MEXC|CoinEx|Uphold|Nexo|Exodus|Trezor Suite|Ledger Live|Trust Wallet|MetaMask|Rabby Wallet|Phantom Wallet|Coinbase Wallet|Rainbow Wallet|Safe Wallet|CoinStats|CoinMarketCap|CoinGecko|Koinly|CoinTracker|CoinLedger|TaxBit|Fold App|Kraken Pro|Bitget|BingX|Crypto Tax Calculator|Zerion".split("|"),
    "Obrazovanje": "Udacity|FutureLearn|OpenClassrooms|Treehouse|Frontend Masters|Egghead.io|Scrimba|Exercism|LeetCode Premium|HackerRank|Codewars|Interview Cake|Educative|A Cloud Guru|Cloud Academy|Linux Academy|Brilliant.org|Memrise|Busuu|Mondly|Drops|Language Drops|Mango Languages|Preply|italki|Cambly|Outschool|Domestika|CreativeLive|Craftsy|The Open University|MIT OpenCourseWare|OpenSesame|MasterClass at Work|Dataquest".split("|"),
    "Zdravlje i fitness": "Les Mills+|Alo Moves|FitOn Pro|Daily Burn|Beachbody on Demand|Tone It Up|Centr|Fitbod|Strong App|Hevy Premium|JEFIT|Strava Summit|TrainingPeaks Premium|Final Surge|Wahoo SYSTM|Rouvy|TrainerRoad|Nike Run Club Premium|Adidas Running Premium|MapMyRun Premium|Runkeeper Go|Sweat|Kayla Fitness|EvolveYou|Fiit App|Glo Yoga|Down Dog Premium|Insight Timer|Noom|Peloton App|Freeletics|Centr Unleashed|AllTrails+|Calm Premium|Headspace Plus".split("|"),
    "Putovanja": "Hopper|Skyscanner Plus|Kiwi.com|Opodo|eDreams|Lastminute.com|TravelPerk|Navan|Expedia One Key|Hotels.com One Key|Vrbo One Key|Marriott Bonvoy|Hilton Honors|IHG One Rewards|Accor ALL|Radisson Rewards|Wyndham Rewards|World of Hyatt|Air France Flying Blue|Lufthansa Miles & More|British Airways Executive Club|KLM Flying Blue|Rail Europe|Trainline|Omio Plus|Rome2Rio|GetYourGuide|Klook|TripIt Pro|Priority Pass|LoungeKey|Airalo|Nomad eSIM|Holafly|Saily eSIM".split("|"),
    "Mobilne usluge": "Lycamobile|Lebara|giffgaff|Mint Mobile|Visible|Google Fi|VOXI|EE|O2 UK|Three UK|Orange|SFR|Bouygues Telecom|Free Mobile|TIM Italia|Vodafone Italia|Iliad Italy|Telekom Deutschland|Congstar|ALDI TALK|simyo|Blau|Tello|US Mobile|Cricket Wireless|Metro by T-Mobile|Boost Mobile|Straight Talk|Tracfone|Verizon Prepaid|AT&T Prepaid|T-Mobile Prepaid|Red Pocket|Ting Mobile|TextNow".split("|"),
    "Pametni dom": "SmartThings|SmartThings Find|Aqara Home|Homey Pro|Smart Life|Tuya|eWeLink|Sonoff|SwitchBot|Kasa Smart|Meross|Nanoleaf|Govee|Wyze Cam Plus|Reolink Cloud|Blink Subscription|Nest Aware Plus|Ecobee Smart Security|Yale Access|August Home|Schlage Home|Bosch Smart Home|Somfy TaHoma|IKEA Home smart|Dyson Link|Roborock|Dreamehome|iRobot Home|Home Connect|LG ThinQ|Miele App|Eufy Clean|Tapo Care|Ring Home|Arlo Secure".split("|"),
    "Auto": "OnStar|FordPass|FordPass Connect|myChevrolet|myGMC|myCadillac|Hyundai Bluelink|Kia Connect|Genesis Connected Services|NissanConnect|INFINITI InTouch|Mazda Connected Services|HondaLink|AcuraLink|Subaru STARLINK|Lexus Enform|myAudi|Audi connect|Volvo Cars app|Volkswagen We Connect|MINI Connected|Jeep Connect|Ram Connect|Fiat Uconnect|Peugeot Services|Citroën Services|Renault Connect|Dacia Media Control|BMW ConnectedDrive|Mercedes me|Porsche Connect|Toyota Connected|Škoda Connect|Tesla Premium Connectivity|Polestar Connect".split("|"),
    "Nadzor": "Pingdom|Site24x7|StatusCake|HetrixTools|Freshping|Hyperping|Checkly|Cronitor|Better Stack|PagerDuty|Opsgenie|VictorOps|xMatters|Incident.io|Rootly|FireHydrant|Atlassian Statuspage|Instatus|Cachet|Uptime Kuma|Cabot|Healthchecks.io|Dead Man's Snitch|Sentry.io|Rollbar|Bugsnag|Honeybadger|Raygun|AppSignal|Elastic Observability|Splunk Observability|Dynatrace|Datadog|New Relic|Grafana Cloud".split("|"),
}

for category, names in GLOBAL_SERVICE_EXPANSION.items():
    for name in names:
        normalized = name.strip()
        if normalized:
            SERVICE_CATALOG.setdefault(normalized, category)
