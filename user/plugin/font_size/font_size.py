import logging
from pathlib import Path
import sass

# Initialize logger
logger = logging.getLogger(__name__)

# --- Configuration Loading ---
try:
    from user.plugin.font_size.font_size_config import (
        ENABLED_DESKTOP,
        ENABLED_MOBILE,
        DESKTOP_FONT_SIZE_PERCENT,
        MOBILE_FONT_SIZE_PERCENT,
        MOBILE_BREAKPOINT_PX
    )
    logger.debug("Font Size config loaded successfully.")
except ImportError:
    logger.warning("Could not import from font_size_config.py. Plugin will be disabled.")
    ENABLED_DESKTOP = False
    ENABLED_MOBILE = False
    DESKTOP_FONT_SIZE_PERCENT = 100
    MOBILE_FONT_SIZE_PERCENT = 100
    MOBILE_BREAKPOINT_PX = 800

def generate_font_size_css():
    """
    Generates or removes the font_size.css file by compiling SCSS
    with variables from the configuration.
    """
    try:
        plugin_dir = Path(__file__).parent
        css_dir = plugin_dir / "css"
        scss_template_path = css_dir / "_font_size.scss"
        css_output_path = css_dir / "font_size.css"

        css_dir.mkdir(exist_ok=True)

        # If both are disabled, ensure the file is empty or deleted
        if not ENABLED_DESKTOP and not ENABLED_MOBILE:
            if css_output_path.exists():
                css_output_path.unlink()
                logger.info("Font Size plugin is fully disabled. Removed existing CSS file.")
            return

        if not scss_template_path.exists():
            logger.error(f"SCSS template not found at {scss_template_path}. Cannot generate CSS.")
            return

        # 1. Create SCSS variable definitions from config
        scss_variables = f"""
$enable-desktop: {'true' if ENABLED_DESKTOP else 'false'};
$enable-mobile: {'true' if ENABLED_MOBILE else 'false'};
$desktop-font-size: {DESKTOP_FONT_SIZE_PERCENT}%;
$mobile-font-size: {MOBILE_FONT_SIZE_PERCENT}%;
$mobile-breakpoint: {MOBILE_BREAKPOINT_PX}px;
"""

        # 2. Read the SCSS template file
        scss_template = scss_template_path.read_text(encoding='utf-8')

        # 3. Combine variables and template
        full_scss_content = scss_variables + scss_template

        # 4. Compile the SCSS to CSS
        compiled_css = sass.compile(string=full_scss_content)

        # 5. Write the final CSS file
        css_output_path.write_text(compiled_css, encoding='utf-8')
        logger.info(f"Successfully compiled SCSS and generated font_size.css.")

    except Exception as e:
        logger.error(f"An error occurred in generate_font_size_css: {e}", exc_info=True)

def register(extensions, extension_configs):
    """
    Entry point called by the CMS. This triggers the CSS generation.
    """
    logger.info("Registering Font Size plugin...")
    generate_font_size_css()
    
    # This plugin doesn't modify Markdown, so it returns the inputs as-is.
    return extensions, extension_configs
