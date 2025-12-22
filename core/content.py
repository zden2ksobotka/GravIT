# core/content.py - Content Processing Logic
import markdown
import re
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from core.cache import PAGE_CACHE
from core.plugins import MARKDOWN_EXTENSIONS, MARKDOWN_EXTENSION_CONFIGS, CONTENT_PROCESSORS

logger = logging.getLogger(__name__)


def _process_image_attributes(html_content: str) -> str:
    """
    Finds image tags containing URL parameters and rewrites them to add HTML attributes 
    (width, height) and CSS classes (align).
    
    Supported parameters:
    - ?width=XXX: Adds width="XXX" and height="auto".
    - &align=center|left|right: Adds class="align-center|left|right".
    """
    def _add_attributes(match):
        img_tag_start = match.group(1) # <img alt="..." src="
        full_url = match.group(2) # The full image URL with query string
        
        # 1. Parse URL to get parameters and clean URL
        
        # Markdown parser escapoval ampersand (&) na &amp;
        unescaped_url = full_url.replace('&amp;', '&')

        url_parts = urlparse(unescaped_url)
        query_params = parse_qs(url_parts.query)
        
        # Clean URL is path only, including scheme/netloc if present
        clean_url = url_parts.path
        if url_parts.scheme and url_parts.netloc:
             clean_url = url_parts.scheme + '://' + url_parts.netloc + url_parts.path

        # 2. Collect attributes and classes
        new_attributes = ""
        new_classes = ""

        # --- Handle width/resize ---
        # The 'width' parameter is used to explicitly set the width of the image element.
        if 'width' in query_params:
            width = query_params['width'][0]
            new_attributes += f' width="{width}" height="auto"'
        
        # --- Handle align ---
        if 'align' in query_params:
            align_value = query_params['align'][0].lower()
            if align_value in ['center', 'left', 'right']:
                new_classes += f' align-{align_value}'
        
        # 3. Reconstruct the tag
        # Group 3: " (closing quote of src)
        tag_end_quote = match.group(3) 
        tag_remainder = match.group(4) # e.g. alt="..."
        tag_closer = match.group(5) # e.g. /> or >
        
        # A) Handle classes (merge new_classes with existing class attribute)
        final_classes = new_classes.strip()
        tag_remainder_cleaned = tag_remainder

        # Zkontrolujeme, zda v remaining atributech již existuje class
        # Musíme použít un-greedy match pro class="..."
        class_match = re.search(r' class=["\']([^"\']*)["\']', tag_remainder)
        
        if class_match:
            # Připojíme k existující třídě a odstraníme starý atribut class z tag_remainder
            existing_classes = class_match.group(1)
            final_classes = (existing_classes + ' ' + final_classes).strip()
            # Odstranění starého atributu class z tag_remainder_cleaned
            tag_remainder_cleaned = re.sub(r'\s*class=["\'][^"\']*?["\']', '', tag_remainder_cleaned, 1)

        # B) Odstranění potenciálně duplicitních width/height z tag_remainder, 
        # pokud tam náhodou byly už od Markdown parseru
        tag_remainder_cleaned = re.sub(r'\s*width=["\'][^"\']*?["\']', '', tag_remainder_cleaned)
        tag_remainder_cleaned = re.sub(r'\s*height=["\'][^"\']*?["\']', '', tag_remainder_cleaned)

        # C) Vytvoření finálního atributu class (pokud existuje)
        final_class_attr = f' class="{final_classes}"' if final_classes else ''
        
        # D) Kombinace nových atributů pro injekci
        injection = new_attributes.strip()
        if injection and final_class_attr:
            injection += " " + final_class_attr.strip()
        elif final_class_attr:
            injection = final_class_attr.strip()

        # E) Final construction: 
        # [start of tag] + [clean src] + [closing src quote] + [new attributes] + [existing attributes] + [closer]
        final_tag = f'{img_tag_start}{clean_url}{tag_end_quote} {injection} {tag_remainder_cleaned} {tag_closer}'
        
        # F) Cleanup: Odstranění nadbytečných mezer, standardizace na non-self closing tag
        final_tag = re.sub(r'\s+', ' ', final_tag).strip()
        # Odstranění potenciálního '/>' a nahrazení '>' pro non-self closing, aby šel správně aplikovat float/margin
        final_tag = re.sub(r'(\s*/?>)$', '>', final_tag)
        
        return final_tag



    # Regex to find <img ... src="path?query" ... >
    # Group 1: (<img[^>]*?src=")
    # Group 2: ([^" ]+?\?[^" ]*?) -> The full src content with query (e.g. /path/to/img.jpg?resize=200&align=center)
    # Group 3: (") -> The closing quote of the src attribute
    # Group 4: (.*?) -> The remainder of the tag before the closing marker (e.g., ' alt=".."')
    # Group 5: (\s*/?>) -> The closing marker (e.g., ' />' or '>')
    return re.sub(r'(<img[^>]*?src=")([^" ]+?\?[^" ]*?)(")(.*?)(\s*/?>)', _add_attributes, html_content)


def get_page_data(page_path: str):
    """Retrieves page data from the cache and converts its Markdown content to HTML."""
    logger.debug(f"get_page_data: Attempting to retrieve page data for path='{page_path}'")
    page_key = page_path.lower()
    cached_data = PAGE_CACHE.get(page_key)
    if not cached_data:
        logger.debug(f"get_page_data: No cached data found for page_key='{page_key}'. Returning None.")
        return None

    md_content = cached_data.get("markdown_content", "")
    page_meta = cached_data.get("page", {})

    # Make copies to avoid modifying the global configs
    page_extensions = MARKDOWN_EXTENSIONS[:]
    page_extension_configs = {k: v.copy() for k, v in MARKDOWN_EXTENSION_CONFIGS.items()}

    # --- Apply Content Processors from Plugins ---
    for processor in CONTENT_PROCESSORS:
        try:
            md_content, page_meta, page_extensions, page_extension_configs = processor(
                md_content, page_meta, page_extensions, page_extension_configs
            )
        except Exception as e:
            logger.error(f"Error applying content processor {processor.__module__}: {e}", exc_info=True)


    if not md_content:
        logger.warning(f"get_page_data: Markdown content is empty for page_key='{page_key}'. Returning empty HTML.")
        return {"page": page_meta, "content": "", "sort_key": cached_data.get("sort_key"), "file_path": cached_data.get("file_path")}

    try:
        md_parser = markdown.Markdown(extensions=page_extensions, extension_configs=page_extension_configs)
        html_content = md_parser.convert(md_content)
        logger.debug(f"get_page_data: Markdown content converted to HTML for page_key='{page_key}'.")
        
        file_path = Path(cached_data.get("file_path", ""))
        if file_path.exists():
            base_dir = Path("user/pages").resolve()
            full_relative_path = file_path.relative_to(base_dir).parent
            base_image_path = f"/user/pages/{full_relative_path}"
            
            # 1. Fix relative paths for all local images.
            # This regex ensures we only prepend the base path if the src does not start with a slash or protocol.
            html_content = re.sub(r'(<img[^>]*?src=")(?!/)(?!https?://)', rf'\1{base_image_path}/', html_content)

            # 2. Call the dedicated function to handle image tag attributes (resize, align)
            html_content = _process_image_attributes(html_content)

            # 3. Global normalization: Ensure all <img> are non-self closing (for CSS alignment compatibility)
            # Replaces <img ... /> with <img ... >
            html_content = re.sub(r'(<img[^>]*?)\s*/>', r'\1>', html_content)

        # Prepare the data to be returned
        return_data = {
            "page": page_meta,
            "content": html_content,
            "sort_key": cached_data.get("sort_key"),
            "file_path": cached_data.get("file_path")
        }
        logger.debug(f"get_page_data: Successfully prepared data for page_key='{page_key}'.")
        return return_data
    except Exception as e:
        logger.error(f"get_page_data: Error processing Markdown or adjusting image paths for page_key='{page_key}': {e}", exc_info=True)
        return None