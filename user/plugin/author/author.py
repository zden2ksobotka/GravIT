import logging
from datetime import datetime

# A global to hold the function that can retrieve the main cache
GET_FULL_PAGE_CACHE = None

def _format_date(date_obj) -> str | None:
    """
    Safely formats a date object, which can be a datetime, timestamp, or string,
    into a 'YYYY-MM-DD' string.
    """
    if not date_obj:
        return None

    if isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d')
    
    if isinstance(date_obj, (int, float)):
        try:
            return datetime.fromtimestamp(date_obj).strftime('%Y-%m-%d')
        except (ValueError, OSError):
            return None # Handle invalid timestamps
            
    # As a fallback for strings, split and take the first part.
    return str(date_obj).split(' ')[0]

def get_author_signature(page_slug: str) -> str:
    """
    Generates an HTML signature string by directly accessing flattened page metadata.
    """
    global GET_FULL_PAGE_CACHE
    logger = logging.getLogger(__name__)

    if not GET_FULL_PAGE_CACHE:
        logger.error("Author Plugin: Main page cache accessor not available.")
        return ""

    main_page_cache = GET_FULL_PAGE_CACHE()
    if not main_page_cache:
        logger.warning("Author Plugin: Main PAGE_CACHE is empty. Cannot retrieve any page data.")
        return ""

    if not page_slug or page_slug not in main_page_cache:
        return ""

    page_data = main_page_cache[page_slug]

    author_name = page_data.get('_page.taxonomy.author') # Corrected key
    date_obj = page_data.get('_page.date')

    signature_parts = []
    if author_name:
        signature_parts.append(str(author_name))
    
    formatted_date = _format_date(date_obj)
    if formatted_date:
        signature_parts.append(formatted_date)

    if not signature_parts:
        return ""

    signature = ", ".join(signature_parts)
    return f'<div class="author-sign">{signature}</div>'

def register_routes(app, templates, theme_config, cms_theme, get_full_page_cache):
    """
    This function is called by main.py during plugin loading.
    It stores the main cache accessor and registers functions for Twig.
    """
    global GET_FULL_PAGE_CACHE
    GET_FULL_PAGE_CACHE = get_full_page_cache
    
    templates.env.globals['get_author_signature'] = get_author_signature
