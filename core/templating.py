# core/templating.py - Template Context and Rendering
from datetime import datetime
from fastapi import Request
from fastapi.templating import Jinja2Templates
from config import THEME_SKIN
from core.security import get_current_user
from core.plugins import ACTIVE_PLUGINS, ACTIVE_PLUGIN_NAMES
from urllib.parse import quote_plus

# --- Global Variables ---
# The searchpath is a list, so Jinja2 will look in both the theme's template 
# directory and the root plugin directory for templates.
templates = Jinja2Templates(directory=[f"{THEME_SKIN}/templates", "user/plugin"])
THEME_CONFIG = {} # This will be populated from main.py

# Add a custom filter for URL encoding to the Jinja2 environment
templates.env.filters['url_encode'] = lambda value: quote_plus(str(value))

# --- Template Context Builder ---
def get_base_template_context(request: Request, nav_builder) -> dict:
    """Builds the base context dictionary for Jinja2 templates."""
    current_user = get_current_user(request)
    main_navigation = nav_builder.get_menu_data(current_user=current_user) if nav_builder else []
    
    return {
        "request": request,
        "current_user": current_user,
        "main_navigation": main_navigation,
        "theme": THEME_CONFIG,
        "theme_path": THEME_SKIN,
        "site_name": THEME_CONFIG.get("name", "CMS"),
        "site_url": str(request.base_url),
        "current_year": datetime.now().year,
        "plugins": ACTIVE_PLUGINS,
        "active_plugin_names": ACTIVE_PLUGIN_NAMES,
    }
