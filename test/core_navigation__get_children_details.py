import sys
import os
import json
import logging

# Přidání kořenového adresáře projektu do PYTHONPATH pro správné importy
sys.path.insert(0, os.path.abspath('.'))

from core.navigation import NavigationBuilder
from core.cache import build_page_cache, build_user_accounts_cache, PAGE_CACHE, USER_ACCOUNTS_CACHE
from core.security import get_page_access_by_spec_rules

# --- Konfigurace DEBUG režimu ---
DEBUG = False # Nastavte na False pro méně detailní výstup

# Konfigurace loggeru - nastavit na DEBUG pro maximální výpis
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(name)s: %(message)s')

logger = logging.getLogger(__name__)

# Nastavte úroveň logování pro konkrétní moduly na DEBUG
logging.getLogger('core.cache').setLevel(logging.DEBUG)
logging.getLogger('core.security').setLevel(logging.DEBUG)

def run_test():
    logger.info("Spouštění testu get_children_details...")

    # 1. Načtení cache (použití reálných dat)
    logger.info("Budování PAGE_CACHE z reálných dat (user/pages)...")
    
    # Explicitní resetování PAGE_CACHE před budováním
    PAGE_CACHE.clear()

    # Odstraníme nastavení PAGES_DIR, aby se použilo výchozí (user/pages)
    if 'PAGES_DIR' in os.environ:
        del os.environ['PAGES_DIR']
    
    build_page_cache()
    build_user_accounts_cache()

    logger.info(f"PAGE_CACHE obsahuje {len(PAGE_CACHE)} stránek.")
    
    # 2. Inicializace NavigationBuilder
    nav_builder = NavigationBuilder(PAGE_CACHE, get_page_access_by_spec_rules)
    logger.info("NavigationBuilder inicializován.")

    # 3. Simulace aktuálního uživatele (přihlášený uživatel s oprávněním site.login: true a zden2k.login: true)
    # ZDE POUŽÍVÁME reálný user/accounts/zden2k.yaml
    current_user = {"username": "zden2k", "access": USER_ACCOUNTS_CACHE.get('zden2k', {}).get('access', {})}
    if not current_user['access']:
        logger.warning("VAROVÁNÍ: Načtená práva pro zden2k jsou prázdná. Test nemusí správně ověřit access control.")

    # 4. Definice očekávaných výstupů dle aktuální struktury
    
    # Očekávaný výstup pro /linux
    # Testovací stránky 'linux' a 'iscsi-fb' neexistují, očekáváme prázdný seznam.
    expected_output_linux = []

    # Očekávaný výstup pro root /
    # Musí obsahovat všechny položky nejvyšší úrovně
    expected_output_root = [
        '{"title": "Blog", "url": "/blog", "slug": "blog", "has_children": true}',
        '{"title": "Home", "url": "/home", "slug": "home", "has_children": false}',
        '{"title": "Install", "url": "/install", "slug": "install", "has_children": false}',
        '{"title": "Documentation", "url": "/doku", "slug": "doku", "has_children": true}',
        '{"title": "Support Hidden", "url": "/support", "slug": "support", "has_children": false}'
    ]

    # Očekávaný výstup pro /doku (testujeme zanoření)
    expected_output_doku = [
        '{"title": "First Level", "url": "/doku/first-level", "slug": "first-level", "has_children": true}',
        '{"title": "How It Works?", "url": "/doku/how-it-works", "slug": "how-it-works", "has_children": true}'
    ]

    test_cases = [
        {"identifier": "linux", "description": "slug 'linux' (neexistující)", "expected": expected_output_linux},
        {"identifier": "/linux", "description": "URL '/linux' (neexistující)", "expected": expected_output_linux},
        {"identifier": "/", "description": "root URL '/", "expected": expected_output_root},
        {"identifier": "doku", "description": "slug 'doku'", "expected": expected_output_doku},
    ]

    all_tests_passed = True
    output_dir = "test/"
    os.makedirs(output_dir, exist_ok=True)

    for case in test_cases:
        identifier = case['identifier']
        description = case['description']
        expected_output = case['expected']
        
        # Adjust identifier for filename to be filesystem-friendly
        filename_identifier = identifier.replace('/', '_').strip('_') if identifier else "root"
        if not filename_identifier:
            filename_identifier = "root"

        expected_output_parsed = sorted([json.loads(s) for s in expected_output], key=lambda x: x['slug'])
        
        if DEBUG:
            logger.info(f"\n--- Testovací případ: {description} (parent_identifier: {identifier}) ---")
        
        # Volání get_children_details
        children_details = nav_builder.get_children_details(parent_identifier=identifier, current_user=current_user)

        actual_output_parsed = sorted([json.loads(s) for s in children_details], key=lambda x: x['slug'])

        # Uložení očekávaného výstupu
        expected_file_path = os.path.join(output_dir, f"{filename_identifier}_ocekavany.txt")
        with open(expected_file_path, 'w', encoding='utf-8') as f:
            json.dump(expected_output_parsed, f, indent=2, ensure_ascii=False)
        logger.info(f"Očekávaný výstup uložen do: {expected_file_path}")

        # Uložení skutečného výstupu
        actual_file_path = os.path.join(output_dir, f"{filename_identifier}_skutecny.txt")
        with open(actual_file_path, 'w', encoding='utf-8') as f:
            json.dump(actual_output_parsed, f, indent=2, ensure_ascii=False)
        logger.info(f"Skutečný výstup uložen do: {actual_file_path}")

        # Porovnání výstupu
        if actual_output_parsed == expected_output_parsed:
            logger.info(f"TEST PASSED pro {description}")
        else:
            logger.error(f"TEST FAILED pro {description}")
            all_tests_passed = False

    if all_tests_passed:
        logger.info("\nVŠECHNY TESTY PROŠLY ÚSPĚŠNĚ!")
        sys.exit(0)
    else:
        logger.error("\nNĚKTERÉ TESTY SELHALY!")
        sys.exit(1)

    logger.info("Test dokončen.")

if __name__ == "__main__":
    run_test()