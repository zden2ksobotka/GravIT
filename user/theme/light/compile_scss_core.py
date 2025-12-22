#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    import sass
except ImportError:
    print("Fatal Error: 'libsass' module not found in the virtual environment.")
    print(f"Attempted to run with: {sys.executable}")
    print("Please ensure it's installed by running './venv/bin/pip install libsass'")
    sys.exit(1)

# Determine project root relative to this script file
# Script is in /user/theme/light, so root is 3 levels up.
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

try:
    from user.theme.light.theme_config import DESKTOP_PAGE_SIZE, IMAGE_DEFAULT_SIZE
except ImportError as e:
    print(f"Error: Could not import project configuration. Details: {e}")
    sys.exit(1)

theme_path = Path(__file__).parent.resolve()
scss_file = theme_path / 'css' / 'style.scss'
css_file = theme_path / 'css' / 'style.css'

if not scss_file.exists():
    print(f"Error: SCSS file not found at {scss_file}")
    sys.exit(1)

try:
    py_vars = f"""
$py-image-default-size: {IMAGE_DEFAULT_SIZE}px;
$py-desktop-page-size: {DESKTOP_PAGE_SIZE}px;
"""
    
    scss_content = scss_file.read_text(encoding='utf-8')
    full_scss = py_vars + "\n" + scss_content
    
    include_paths = [str(theme_path / 'css')] 
    
    compiled_css = sass.compile(string=full_scss, include_paths=include_paths)
    
    css_file.write_text(compiled_css, encoding='utf-8')
    
    relative_scss = scss_file.relative_to(project_root)
    relative_css = css_file.relative_to(project_root)
    print(f'Successfully compiled {relative_scss} to {relative_css}')

except Exception as e:
    print(f'Error compiling SCSS: {e}')
    sys.exit(1)
