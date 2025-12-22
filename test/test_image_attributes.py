import re
from core.content import _process_image_attributes
from urllib.parse import urlparse, parse_qs

# --- Testovací scénáře pro _process_image_attributes ---

def test_process_image_attributes():
    print("--- Testování _process_image_attributes (izolovaný test) ---")

    # Scénář 1: Resize a Align
    html_input_1 = '<img alt="Gravit" src="/user/pages/001.Home/gravit_code.png?width=300&align=center" />'
    expected_output_1 = '<img alt="Gravit" src="/user/pages/001.Home/gravit_code.png" width="300" height="auto" class="align-center">'
    result_1 = _process_image_attributes(html_input_1)
    
    # Normalizace výsledku pro porovnání
    result_1 = re.sub(r'\s+', ' ', result_1).strip()
    expected_output_1 = re.sub(r'\s+', ' ', expected_output_1).strip()
    
    is_ok_1 = result_1 == expected_output_1
    print(f"Test 1 (Resize & Center): {'PASS' if is_ok_1 else 'FAIL'}")
    if not is_ok_1:
        print(f"  Očekáváno: {expected_output_1}")
        print(f"  Získáno:   {result_1}")
        print("-" * 20)

    # Scénář 2: Pouze Align Right, se zadaným class
    html_input_2 = '<img alt="Test" src="/path/to/img.jpg?align=right" class="existing-class" />'
    expected_output_2 = '<img alt="Test" src="/path/to/img.jpg" class="existing-class align-right">'
    result_2 = _process_image_attributes(html_input_2)
    
    result_2 = re.sub(r'\s+', ' ', result_2).strip()
    expected_output_2 = re.sub(r'\s+', ' ', expected_output_2).strip()
    
    is_ok_2 = result_2 == expected_output_2
    print(f"Test 2 (Align Right & Class): {'PASS' if is_ok_2 else 'FAIL'}")
    if not is_ok_2:
        print(f"  Očekáváno: {expected_output_2}")
        print(f"  Získáno:   {result_2}")
        print("-" * 20)

    # Scénář 3: Pouze Resize
    html_input_3 = '<img alt="Only Resize" src="/path/to/img.jpg?width=100" />'
    expected_output_3 = '<img alt="Only Resize" src="/path/to/img.jpg" width="100" height="auto">'
    result_3 = _process_image_attributes(html_input_3)
    
    result_3 = re.sub(r'\s+', ' ', result_3).strip()
    expected_output_3 = re.sub(r'\s+', ' ', expected_output_3).strip()

    is_ok_3 = result_3 == expected_output_3
    print(f"Test 3 (Only Resize): {'PASS' if is_ok_3 else 'FAIL'}")
    if not is_ok_3:
        print(f"  Očekáváno: {expected_output_3}")
        print(f"  Získáno:   {result_3}")
        print("-" * 20)

    # Scénář 4: Původní HTML bez úprav (funkce by ho měla nechat beze změny)
    html_input_4 = '<img alt="No Change" src="/path/to/img.jpg" />'
    expected_output_4 = '<img alt="No Change" src="/path/to/img.jpg" />' # Očekáváme nezměněný self-closing tag
    result_4 = _process_image_attributes(html_input_4)
    
    result_4 = re.sub(r'\s+', ' ', result_4).strip()
    expected_output_4 = re.sub(r'\s+', ' ', expected_output_4).strip()

    is_ok_4 = result_4 == expected_output_4
    print(f"Test 4 (No Change - No Query String): {'PASS' if is_ok_4 else 'FAIL'}")
    if not is_ok_4:
        print(f"  Očekáváno: {expected_output_4}")
        print(f"  Získáno:   {result_4}")
        print("-" * 20)

    print("-" * 40)
    if is_ok_1 and is_ok_2 and is_ok_3 and is_ok_4:
        print("Všechny izolované testy prošly.")
    else:
        print("Některé testy selhaly. Je třeba oprava.")

if __name__ == "__main__":
    # Nastavení dummy loggeru, aby test neházel chyby při importu z core
    class DummyLogger:
        def debug(self, msg, *args): pass
        def info(self, msg, *args): pass
        def warning(self, msg, *args): pass
        def error(self, msg, *args, **kwargs): print(f"ERROR: {msg}")

    # Patch pro simulaci prostředí a zamezení chyb při importu loggeru v core
    import core.content
    core.content.logger = DummyLogger()

    test_process_image_attributes()
    # Poznámka: testování get_page_data je komplikované kvůli závislosti na PAGE_CACHE a Markdown parseru.
    # Proto se zaměříme na izolovaný test _process_image_attributes, který je klíčem k problému.

