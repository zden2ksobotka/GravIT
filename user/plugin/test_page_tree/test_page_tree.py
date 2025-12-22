import logging
from fastapi import Request
from fastapi.responses import HTMLResponse
from markupsafe import Markup
from user.plugin.test_page_tree.test_page_tree_config import PAGE_TREE_ENABLED, PAGE_TREE_ALL_VISIBLE, PAGE_TREE_TITLE

logger = logging.getLogger(__name__)

def register_routes(app, get_nav_builder):
    """
    Registers a new route /tree that returns a raw HTML fragment 
    of the page sitemap, similar to the /search endpoint.
    """
    
    if not PAGE_TREE_ENABLED:
        logger.info("test_page_tree plugin is disabled by configuration.")
        return

    @app.get("/tree", response_class=HTMLResponse)
    async def test_page_tree(request: Request):
        logger.info("--- Raw page tree request received on /tree ---")
        
        try:
            # Import get_current_user dynamically from main, as recommended for plugins
            from main import get_current_user
            current_user = get_current_user(request)
            nav_builder = get_nav_builder()
            
            # The logic now correctly passes the show_all flag to the central NavigationBuilder
            page_tree_html = nav_builder.get_search_tree_html(
                current_user=current_user, 
                show_all=PAGE_TREE_ALL_VISIBLE
            ) if nav_builder else ""
            
            # Combine title and tree into a single HTML fragment
            html_fragment = f'<h3 class="title is-4">{PAGE_TREE_TITLE}</h3>\n{page_tree_html}'
            
            return HTMLResponse(content=html_fragment)

        except Exception as e:
            logger.error(f"--- CRITICAL ERROR during raw page tree generation: {e} ---", exc_info=True)
            return HTMLResponse(content="<p>Error generating sitemap.</p>", status_code=500)

