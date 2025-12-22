import logging
import pprint
from fastapi import Request
from fastapi.responses import HTMLResponse

# Import the cache directly for debugging
from core.cache import PAGE_CACHE

logger = logging.getLogger(__name__)

PAGE_TREE_TITLE = "Dropdown Menu Test (Python Rendered)"

def render_dropdown_html(menu_items: list, level: int = 0) -> str:
    """
    Recursively renders the menu data into an HTML string that mimics the main theme's navigation.
    Only processes levels 0 and 1.
    """
    if not menu_items or level > 1:
        return ""

    # Level 0 is a list of <a> tags inside a <section>
    if level == 0:
        html = ''
        for item in menu_items:
            has_children = bool(item.get("children"))
            html += '<div class="nav-item-wrapper">' # Wrapper for each top-level item
            if has_children:
                html += '<li class="nav-item has-submenu">'
                html += f'<a href="{item["url"]}">{item["title"]}</a>'
                html += render_dropdown_html(item["children"], level + 1)
                html += '</li>'
            else:
                html += f'<a href="{item["url"]}" class="nav-item">{item["title"]}</a>'
            html += '</div>'
        return html
    
    # Level 1 is a <ul> with <li>
    else: # level == 1
        html = '<ul class="submenu">'
        for item in menu_items:
            html += f'<li><a href="{item["url"]}">{item["title"]}</a></li>'
        html += '</ul>'
        return html

def register_routes(app, get_nav_builder, templates, logger_instance):
    global logger
    logger = logger_instance
    """
    Registers a new route /tree2 that returns a page with a 
    dropdown menu mimicking the main site's header.
    """
    @app.get("/tree2", response_class=HTMLResponse)
    async def page_tree2(request: Request):
        logger.info("--- Dropdown menu test request received (Full Header Mimic) ---")
        
        # --- DEBUG: Print a specific PAGE_CACHE entry ---
        try:
            acmesh_page_data = PAGE_CACHE.get('linux/acmesh')
            if acmesh_page_data:
                logger.info("--- START DEBUG: PAGE_CACHE entry for 'linux/acmesh' ---")
                pretty_data = pprint.pformat(acmesh_page_data)
                logger.info(pretty_data)
                logger.info("--- END DEBUG: PAGE_CACHE entry for 'linux/acmesh' ---")
            else:
                logger.warning("--- DEBUG: Could not find 'linux/acmesh' in PAGE_CACHE ---")
        except Exception as e:
            logger.error(f"--- DEBUG: Error while trying to print PAGE_CACHE: {e} ---")
        # --- END DEBUG ---

        try:
            from main import get_current_user
            current_user = get_current_user(request)
            nav_builder = get_nav_builder()
            
            sitemap_data = nav_builder.get_sitemap_data(current_user=current_user) if nav_builder else []
            
            menu_html = render_dropdown_html(sitemap_data)

            # This HTML structure now mimics the theme's header exactly
            full_html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>{PAGE_TREE_TITLE}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
                                                    <link rel="stylesheet" href="/user/theme/light/css/style.css">
                                                    <link rel="stylesheet" href="/user/plugin/test_menu_wrap/css/_test_menu_wrap.css"></head>
<body style="padding: 0;">
    <header class="full-width-header">
        <div class="header-inner-container">
            <nav class="main-nav" id="main-nav">
                <section class="navbar-section left">
                    <a id="search-toggle" class="nav-item" href="#">Search</a>
                    {'''<a href="/logout" class="nav-item">Logout</a>''' if current_user else '''<a href="/login" class="nav-item">Login</a>'''}
                    {'''<span class="nav-item">(<a href="/profile">{current_user.fullname}</a>)</span>''' if current_user else ''''''}
                </section>
                <section class="navbar-section right">
                    {menu_html}
                </section>
            </nav>
        </div>
    </header>
    <div class="container" style="padding-top: 2rem;">
        <h1>Test Content Below Header</h1>
        <p>This area is for content to ensure the header doesn't overlap.</p>
    </div>
</body>
</html>
            """
            return HTMLResponse(content=full_html)

        except Exception as e:
            import traceback
            logger.error(f"--- CRITICAL ERROR during dropdown menu generation: {e} ---", exc_info=True)
            tb_str = traceback.format_exc()
            error_html = f"""
            <h1>Error Generating Dropdown Menu</h1>
            <p>An unexpected error occurred. Please check the application logs.</p>
            <pre style="background-color: #f0f0f0; border: 1px solid #ccc; padding: 10px; border-radius: 5px;">{tb_str}</pre>
            """
            return HTMLResponse(content=error_html, status_code=500)
