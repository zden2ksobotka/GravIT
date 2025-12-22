import os
import sys
import sass

# Přidání kořenového adresáře projektu do PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

def compile_toc_scss():
    """
    Compiles the _toc.scss file into toc.css.
    """
    scss_file_path = os.path.join(os.path.dirname(__file__), 'css', '_toc.scss')
    css_file_path = os.path.join(os.path.dirname(__file__), 'css', 'toc.css')

    try:
        with open(scss_file_path, 'r', encoding='utf-8') as f:
            scss_content = f.read()
    except FileNotFoundError:
        print(f"ERROR: Source SCSS file not found at {scss_file_path}")
        sys.exit(1)

    try:
        compiled_css = sass.compile(string=scss_content)
    except Exception as e:
        print(f"ERROR: SCSS compilation failed: {e}")
        sys.exit(1)

    try:
        with open(css_file_path, 'w', encoding='utf-8') as f:
            f.write(compiled_css)
        print(f"Successfully compiled {scss_file_path} to {css_file_path}")
    except IOError as e:
        print(f"ERROR: Could not write to CSS file at {css_file_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    compile_toc_scss()
