import logging
import sys
from core.content import get_page_data

# Konfigurace logování, aby se zobrazily DEBUG zprávy
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Načtení stránky (předpokládáme, že "home" je klíč pro 001.Home)
# PAGE_CACHE je naplněna při importu z core.cache, což se neprovede, pokud nejdřív nespustíme kód z main.py nebo test.
# Nicméně, get_page_data by se měl pokusit načíst z cache.

# Protože nemohu plně simulovat FastAPI prostředí, zkusím to spustit jen s importem, 
# který by měl vyvolat logger.

# Vzhledem k závislosti na cache, musím nejprve inicializovat cache.

# Zkusím nejdříve simulovat volání get_page_data s klíčem, který se týká '001.Home'
# Zjistím klíč ze souboru, který uživatel uvedl: 001.Home/default.md

# Klíč pro Home je 'cms.n0ip.eu/home' nebo jen 'home'. Dle kontextu to vypada na slug/path.
# Vytvořím dummy klíč, který je pro Home.

PAGE_SLUG = "home" 

print(f"DEBUG: Načítám data pro stránku: {PAGE_SLUG}")
page_data = get_page_data(PAGE_SLUG)

if page_data:
    print("\n--- Výsledek get_page_data (zobrazený content by měl být HTML) ---")
    print(page_data.get("content", "N/A"))
    print("------------------------------------------------------------------")
else:
    print(f"ERROR: Nepodařilo se načíst data pro {PAGE_SLUG}. Pravděpodobně není naplněna cache.")

# Abychom dostali logovací hlášky, musíme zajistit, že se spustí build_page_cache, 
# což je složité bez plného spuštění main.py.

# Zkusím jen volat logger, pokud je potřeba.
# Můj kód se už zloguje.

# Vypnu cache a plugins pro tento test (dočasně):
import core.content
core.content.PAGE_CACHE = {
    'home': {
        'markdown_content': '![Gravit](gravit_code.png?resize=300&align=center)\n![Popisek obrázku](gravit_code.png?resize=100&align=center)',
        'page': {},
        'sort_key': 0,
        'file_path': '/var/www/cms.n0ip.eu/user/pages/001.Home/default.md'
    }
}
core.content.MARKDOWN_EXTENSIONS = [] # Vypnu extension, aby nedošlo k chybám
core.content.MARKDOWN_EXTENSION_CONFIGS = {}
core.content.CONTENT_PROCESSORS = []

print(f"DEBUG: Volám get_page_data s manuálně vytvořeným PAGE_CACHE.")
page_data = get_page_data(PAGE_SLUG)

if page_data:
    print("\n--- Výsledek get_page_data (zobrazený content by měl být HTML) ---")
    print(page_data.get("content", "N/A"))
    print("------------------------------------------------------------------")
else:
    print(f"ERROR: Nepodařilo se načíst data pro {PAGE_SLUG}. Chyba při zpracování.")
