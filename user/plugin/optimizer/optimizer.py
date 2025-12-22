import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_service_worker(cms_theme, active_plugins):
    """
    Generates the service-worker.js file from a template, dynamically injecting
    the list of assets to cache.
    """
    logger.info("Optimizer Plugin: Generating service worker...")
    try:
        # --- Define core assets from the theme ---
        theme_path = Path(cms_theme)
        core_assets = [
            f'/{theme_path.joinpath("css/style.css").as_posix()}',
            f'/{theme_path.joinpath("css/skeleton.css").as_posix()}',
            f'/{theme_path.joinpath("css/atom-one-dark.min.css").as_posix()}',
            f'/{theme_path.joinpath("js/main.js").as_posix()}',
            f'/{theme_path.joinpath("js/highlight.min.js").as_posix()}',
            # External assets
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css',
        ]

        # --- Combine with dynamic plugin assets ---
        all_assets_to_cache = core_assets + active_plugins['css'] + active_plugins['js']
        
        # --- Read template and generate final JS file ---
        # The template is now inside the plugin's own directory
        template_path = Path(__file__).parent / "service-worker.js.tpl"
        # Output the final file into the plugin's directory as well
        output_path = Path(__file__).parent / "service-worker.js"

        if not template_path.exists():
            logger.error("Optimizer Plugin: service-worker.js.tpl not found! Cannot generate.")
            return

        template_content = template_path.read_text(encoding='utf-8')
        
        urls_js_array = json.dumps(all_assets_to_cache, indent=2)
        
        final_content = template_content.replace('__URLS_TO_CACHE__', urls_js_array)
        
        output_path.write_text(final_content, encoding='utf-8')
        logger.info(f"Optimizer Plugin: Successfully generated {output_path} with {len(all_assets_to_cache)} assets.")

    except Exception as e:
        logger.error(f"Optimizer Plugin: Failed to generate service worker: {e}")

def on_startup(cms_theme, active_plugins):
    """
    This function will be called by the main app during the startup event.
    """
    generate_service_worker(cms_theme, active_plugins)

def register(extensions, extension_configs):
    """
    Standard plugin registration function. This plugin doesn't modify Markdown,
    so it just returns the inputs as-is.
    """
    return extensions, extension_configs
