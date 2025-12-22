import sys
import os
import re
import unittest

# Přidání cesty k pluginům a jádru pro import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # Import funkce z pluginu
    from user.plugin.blog.blog import _create_snippet
except ImportError:
    print("ERROR: Nelze importovat _create_snippet. Ujistěte se, že PATH je správná a modul existuje.")
    sys.exit(1)


class TestBlogSnippet(unittest.TestCase):
    """Testuje funkčnost funkce _create_snippet pro ořezávání HTML obsahu."""
    
    def test_snippet_generation_with_html_and_code(self):
        """Testuje, zda se vygeneruje správný úryvek při přítomnosti nadpisů a kódu."""
        chars_limit = 50
        
        # Příklad HTML kódu, který simuluje výstup Markdownu z postu 1
        html_content = """
            <h1>Nadpis 1</h1>
            <h2>Úvod</h2>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
            <h3>Podsekce</h3>
            <pre><code class="language-python"># Příklad kódu
def calculate_pagination(total_items, items_per_page):
    return (total_items + items_per_page - 1) // items_per_page
</code></pre>
            <p>Druhý odstavec.</p>
        """
        
        expected_start = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
        
        snippet = _create_snippet(html_content, chars_limit)
        
        # Očekáváme, že úryvek začíná textem a končí [...]
        self.assertIsNotNone(snippet)
        self.assertNotEqual(snippet.strip(), "", "Úryvek by neměl být prázdný.")
        self.assertLessEqual(len(snippet), chars_limit + 5, "Úryvek je příliš dlouhý.")
        self.assertTrue(snippet.endswith("[...]"), "Úryvek by měl končit s '...'.")
        
        # Kontrola, zda text začíná očekávaným obsahem
        self.assertTrue(snippet.startswith("Lorem ipsum dolor sit amet"), f"Neočekávaný začátek úryvku: {snippet[:30]}")
        
    def test_snippet_empty_input(self):
        """Testuje, že pro prázdný vstup se vrací prázdný řetězec."""
        self.assertEqual(_create_snippet("", 50), "")
        self.assertEqual(_create_snippet("Some text", 0), "")

    def test_snippet_short_text(self):
        """Testuje, že krátký text se nezkracuje a nekončí s [...]"""
        text = "<p>Short text.</p>"
        snippet = _create_snippet(text, 50)
        self.assertEqual(snippet, "Short text.")


if __name__ == '__main__':
    # Spuštění testu s detailním výpisem
    print("--- Spouštění izolačního testu pro _create_snippet ---")
    
    # Nastavení pro zobrazení plného diffu u chyb
    unittest.main(argv=sys.argv[:1], exit=False, verbosity=2)

    
# TENTO TEST BUDE SPUŠTĚN VE VENV POMOCÍ RUN_SHELL_COMMAND
# python3 test/test_blog_snippet.py
