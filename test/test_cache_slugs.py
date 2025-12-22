import sys
import os
import json
import logging

# Konfigurace loggeru
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

from core.cache import build_page_cache, PAGE_CACHE
from core.navigation import NavigationBuilder
from core.security import get_page_access_by_spec_rules

def run_test():
    logger.info("--- Spouštění TESTU: Viditelnost stránek s visible: false v navigaci ---")

    PAGE_CACHE.clear()
    build_page_cache()
    
    # Inicializace NavigationBuilder (pro testování visibility, dummy checker)
    def dummy_access_checker(page_data, user):
        # Vrací None (přístup povolen) pro účely tohoto testu
        return None

    # Dummy uživatel
    current_user = {"username": "test_user", "access": {}}

    nav_builder = NavigationBuilder(PAGE_CACHE, dummy_access_checker)

    # Stránky, které by se v menu NEMĚLY objevit (visible: false v user/pages)
    hidden_slugs = ['home', 'support']
    
    # 1. Test NavigationBuilder.get_menu_data (Musí respektovat visible: false)
    logger.info("Test 1: get_menu_data (musí respektovat visible: false)")
    menu_data = nav_builder.get_menu_data(current_user=current_user)
    
    found_hidden_in_menu = []
    for item in menu_data:
        if item.get('slug') in hidden_slugs:
            found_hidden_in_menu.append(item.get('slug'))

    if not found_hidden_in_menu:
        logger.info("PASS: get_menu_data správně skrylo stránky s visible: false.")
    else:
        logger.error(f"FAIL: get_menu_data obsahuje skryté stránky: {found_hidden_in_menu}")
        sys.exit(1)


    # 2. Test NavigationBuilder.get_search_tree_html (Musí ignorovat visible: false, pokud je show_all=True)
    logger.info("Test 2: get_search_tree_html (musí zobrazit i skryté, pokud je show_all=True)")
    
    # get_search_tree_html vrací HTML string, budeme hledat řetězec URL
    search_tree_html = nav_builder.get_search_tree_html(current_user=current_user, show_all=True)

    missing_hidden_slugs = []
    for slug in hidden_slugs:
        # Hledám, zda se v HTML objevuje odkaz na skrytou stránku
        expected_url = f'/{slug}'
        if expected_url not in search_tree_html:
            missing_hidden_slugs.append(slug)
    
    if not missing_hidden_slugs:
        logger.info("PASS: get_search_tree_html správně zobrazuje skryté stránky s show_all=True.")
    else:
        logger.error(f"FAIL: get_search_tree_html nezobrazuje očekávané skryté stránky: {missing_hidden_slugs}")
        sys.exit(1)
    
    logger.info("--- TESTY USPEŠNĚ DOKONČENY ---")
    sys.exit(0)

if __name__ == "__main__":
    run_test()