# core/plugins.py - Plugin System Logic
import sys
import importlib.util
import logging
from pathlib import Path
import inspect

logger = logging.getLogger(__name__)

# --- Global Variables ---
ACTIVE_PLUGIN_NAMES = []
ACTIVE_PLUGINS = {'css': [], 'js': []}
CONTENT_PROCESSORS = []
MARKDOWN_EXTENSIONS = ['attr_list', 'fenced_code', 'pymdownx.tilde', 'md_in_html', 'pymdownx.tasklist', 'tables']
MARKDOWN_EXTENSION_CONFIGS = {
    'fenced_code': {'lang_prefix': 'language-'},
    'pymdownx.tasklist': {'custom_checkbox': True}
}

# --- Plugin Loading ---
def load_plugins(app, get_nav_builder, templates, theme_config, theme_skin, get_full_page_cache, plugin_dir="user/plugin"):
    """Dynamically loads all plugins from the 'user/plugin' directory."""
    global MARKDOWN_EXTENSIONS, MARKDOWN_EXTENSION_CONFIGS, CONTENT_PROCESSORS
    plugin_path = Path(plugin_dir)
    logger.debug(f"Entering load_plugins. Plugin directory: {plugin_path}")
    if not plugin_path.is_dir():
        logger.warning(f"Plugin directory not found: {plugin_path}")
        return

    logger.info("--- Loading Plugins ---")
    ACTIVE_PLUGIN_NAMES.clear()
    ACTIVE_PLUGINS['css'].clear()
    ACTIVE_PLUGINS['js'].clear()
    CONTENT_PROCESSORS.clear()

    if 'toc' in MARKDOWN_EXTENSIONS:
        MARKDOWN_EXTENSIONS.remove('toc')

    for plugin in sorted(plugin_path.iterdir()):
        if plugin.is_dir():
            plugin_name = plugin.name
            logger.info(f"Processing plugin directory: {plugin_name}")
            plugin_main_file = plugin / f"{plugin_name}.py"
            
            if plugin_main_file.exists():
                try:
                    spec = importlib.util.spec_from_file_location(plugin_name, plugin_main_file)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[plugin_name] = module
                    spec.loader.exec_module(module)
                    
                    ACTIVE_PLUGIN_NAMES.append(plugin_name)
                    logger.info(f"Successfully loaded plugin: {plugin_name}")

                    if hasattr(module, 'register'):
                        MARKDOWN_EXTENSIONS, MARKDOWN_EXTENSION_CONFIGS = module.register(
                            MARKDOWN_EXTENSIONS, MARKDOWN_EXTENSION_CONFIGS
                        )
                        logger.info(f"Executed 'register' for plugin: {plugin_name}")

                    if hasattr(module, 'register_routes'):
                        sig = inspect.signature(module.register_routes)
                        
                        route_args = {
                            "app": app,
                            "get_nav_builder": get_nav_builder,
                            "templates": templates,
                            "theme_config": theme_config,
                            "cms_theme": theme_skin,
                            "get_full_page_cache": get_full_page_cache,
                            "get_active_plugins": lambda: ACTIVE_PLUGIN_NAMES,
                            "logger_instance": logger
                        }
                        
                        valid_args = {k: v for k, v in route_args.items() if k in sig.parameters}
                        module.register_routes(**valid_args)
                        logger.info(f"Registered API routes for plugin: {plugin_name}")

                    if hasattr(module, 'register_content_processor'):
                        processor = module.register_content_processor()
                        if callable(processor):
                            CONTENT_PROCESSORS.append(processor)
                            logger.info(f"Registered content processor for plugin: {plugin_name}")

                    # --- Plugin Template Path Registration ---
                    plugin_template_dir = plugin / 'templates'
                    if plugin_template_dir.is_dir():
                        try:
                            templates.env.loader.searchpath.append(str(plugin_template_dir))
                            logger.debug(f"Added template path for plugin {plugin_name}: {plugin_template_dir.as_posix()}")
                        except Exception as e:
                            logger.error(f"Failed to add template path for {plugin_name}: {e}")

                    css_file = plugin / 'css' / f"{plugin_name}.css"
                    if css_file.exists():
                        ACTIVE_PLUGINS['css'].append(f"/{css_file.as_posix()}")
                        logger.debug(f"Added CSS file for plugin {plugin_name}: {css_file.as_posix()}")
                    
                    js_file = plugin / 'js' / f"{plugin_name}.js"
                    if js_file.exists():
                        ACTIVE_PLUGINS['js'].append(f"/{js_file.as_posix()}")
                        logger.info(f"Added JS file for plugin {plugin_name}: {js_file.as_posix()}")

                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_name}: {e}", exc_info=True)
    logger.info(f"--- Finished Loading Plugins. Active plugins: {ACTIVE_PLUGIN_NAMES} ---")
