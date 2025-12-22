import logging
import math
import json
import re
import markdown
from pathlib import Path

from .blog_config import FALLBACK_ARTICLES_CHARS

from fastapi import APIRouter, Request, HTTPException
from core.templating import get_base_template_context, templates 

logger = logging.getLogger(__name__)

# Router pro blog
blog_router = APIRouter()

def _create_snippet(html_content: str, chars_limit: int = 0) -> str:
    """
    Generates a text snippet from HTML content.
    1. Removes all <pre>...</pre> blocks (code).
    2. Removes all H1-H6 tags (headings).
    3. Removes all other HTML tags.
    4. Cleans up multiple spaces/newlines and HTML entities.
    5. Truncates the text if chars_limit > 0.
    """
    if not html_content or chars_limit <= 0:
        return ""

    # 1. Odstranění všech <pre>...</pre> bloků (kód)
    no_code_html = re.sub(r'<pre>.*?</pre>', '', html_content, flags=re.DOTALL)

    # 2. Odstranění všech H1-H6 nadpisů
    headings_removed = re.sub(r'<h[1-6].*?>.*?</h[1-6]>', '', no_code_html, flags=re.DOTALL).strip()

    # 3. Odstranění všech zbylých HTML tagů
    clean_text = re.sub(r'<[^>]+>', '', headings_removed)
    
    # 4. Odstranění zbytků entit a vícenásobných bílých znaků
    clean_text = re.sub(r'&[^;]+;', ' ', clean_text) # Nahrazení entit mezerou, aby se neslepila slova
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    # 5. Zkrácení na zadaný limit
    if len(clean_text) > chars_limit:
        # Hledání posledního bílého znaku před limitem pro čisté oříznutí
        truncated = clean_text[:chars_limit]
        last_space = truncated.rfind(' ')
        if last_space > 0:
            truncated = truncated[:last_space]
        return f"{truncated.strip()} [...]"
    
    return clean_text

def register_routes(app, get_nav_builder, get_full_page_cache, **kwargs):
    """
    Registruje blog router (pro budoucí API), ale hlavní handler je volán z main.py.
    """
    # Router se neregistruje se specifickou routou, ale spoléháme na to, 
    # že ho bude volat hlavní handler v main.py/read_page
    logger.info("BLOG: Plugin initialized. Dependencies will be passed directly to blog_page_handler from main.py.")
    app.include_router(blog_router)


async def blog_page_handler(request: Request, page_data: dict, page_key: str, page_slug: str, get_nav_builder, get_full_page_cache):
    """
    Hlavní handler, který zpracuje blogovou stránku. 
    Voláno z main.py, pokud má stránka 'blog: true'.
    """
    logger.info(f"BLOG: Processing blog index for page_key: {page_key}")
    
    # KONTROLA A REGISTRACE TEMPLATE CESTY (pro robustnost)
    plugin_template_dir = str(Path(__file__).parent / 'templates')
    if plugin_template_dir not in templates.env.loader.searchpath:
        templates.env.loader.searchpath.insert(0, plugin_template_dir)
        logger.warning(f"BLOG: Manually registered template path: {plugin_template_dir} to Jinja2 searchpath.")

    # Získání nav_builder a cache z getterů
    nav_builder = get_nav_builder()
    page_cache = get_full_page_cache() # PŘÍSTUP K PLOCHÉ CACHE
    
    if nav_builder is None or page_cache is None:
        logger.error("BLOG: NavigationBuilder or PageCache is not yet initialized. Cannot process page.")
        raise HTTPException(status_code=404, detail="Page not found or navigation index not ready.")

    # Získání konfigurace blogu z YAML
    page_meta = page_data.get('page', {})
    
    # Sestavíme blog_config z klíčů s tečkovou notací (např. 'blog.articles_page')
    blog_config = {}
    for key, value in page_meta.items():
        if key.startswith('blog.'):
            blog_config[key[5:]] = value 

    articles_per_page = blog_config.get('articles_page', 10)
    articles_chars = blog_config.get('articles_chars', FALLBACK_ARTICLES_CHARS) # NOVÁ KONFIGURACE. Používá fallback, který je nastaven na 50.

    # Zajištění, že articles_per_page a articles_chars jsou int
    try:
        articles_per_page = int(articles_per_page)
    except (ValueError, TypeError):
        articles_per_page = 10
    
    try:
        articles_chars = int(articles_chars)
    except (ValueError, TypeError):
        articles_chars = 0

    logger.debug(f"BLOG: Config articles_chars loaded as: {articles_chars}")

    # Přejmenování kvůli konzistentnímu použití ve funkcích
    # Aktualizace konfigurace o novou proměnnou
    blog_config.update({'articles_page': articles_per_page, 'articles_chars': articles_chars})
    
    for key, value in page_meta.items():
        if key.startswith('blog.'):
            blog_config[key[5:]] = value
        elif key == 'blog' and isinstance(value, dict):
            # Pro případ, že by byla použita správná YAML syntaxe
            blog_config.update(value)

    # --- Konec úpravy konfigurace ---
    
    # Načtení vnitřního modulu pro get_page_data
    from core.content import get_page_data 
    
    # K získání MARKDOWN_EXTENSIONS a CONFIGS
    from core.plugins import MARKDOWN_EXTENSIONS, MARKDOWN_EXTENSION_CONFIGS

    # 1. Získání všech dětí (příspěvků)
    try:
        children_json_list = nav_builder.get_children_details(
            parent_identifier=page_key, 
            current_user=get_base_template_context(request, nav_builder).get('current_user')
        )
        children_list = [json.loads(s) for s in children_json_list]
    except Exception as e:
        logger.error(f"BLOG: Failed to get children for {page_key}: {e}")
        children_list = []
        
    total_articles = len(children_list)

    # 2. Logika stránkování
    try:
        current_page = int(request.query_params.get('p', 1))
    except ValueError:
        current_page = 1
        
    total_pages = math.ceil(total_articles / articles_per_page)
    current_page = max(1, min(current_page, total_pages or 1)) 
    
    start_index = (current_page - 1) * articles_per_page
    end_index = start_index + articles_per_page
    
    articles_to_display_meta = children_list[start_index:end_index]

    # 3. Získání plného obsahu a generování snippetu
    processed_articles = []
    # Oddělovač v HTML komentáři, jak je požadováno.
    wrap_delimiter = r'<!--- \[WRAP\] --->' 

    for article_meta in articles_to_display_meta:
        article_key = article_meta.get('url', '/').strip('/')
        
        # Získání surového Markdownu
        cached_page = page_cache.get(article_key)
        
        if cached_page:
            raw_markdown = cached_page.get("markdown_content", "")
            
            # 3a. Získání celého obsahu (vždy potřeba pro detail a jako zdroj pro CHARS snippet)
            full_article_data = get_page_data(article_key)
            full_content_html = full_article_data.get('content', "") if full_article_data else ""
            
            if not full_content_html:
                 logger.warning(f"BLOG: Full content is empty for article: {article_key}. Skipping.")
                 continue
            
            final_snippet_html = ""
            
            # 3b. Kontrola explicitního oddělovače WRAP (má prioritu)
            if re.search(wrap_delimiter, raw_markdown, re.IGNORECASE):
                # Použití re.split pro robustní rozdělení, ignorující bílé znaky kolem oddělovače
                markdown_parts = re.split(wrap_delimiter, raw_markdown, 1, re.IGNORECASE)
                markdown_snippet = markdown_parts[0].strip()
                
                # Konverze části Markdownu na HTML
                md_parser = markdown.Markdown(extensions=MARKDOWN_EXTENSIONS, extension_configs=MARKDOWN_EXTENSION_CONFIGS)
                final_snippet_html = md_parser.convert(markdown_snippet)
                
                logger.debug(f"BLOG Article: {article_key}. WRAP DETECTED. RAW MD: {markdown_snippet[:50]}. HTML Len: {len(final_snippet_html)}")

            # 3c. Fallback: Pokud NENÍ generován explicitní úryvek (ani WRAP), použijeme CHARS
            if not final_snippet_html and articles_chars > 0:
                plain_text = _create_snippet(full_content_html, articles_chars)
                if plain_text: # Zkontrolujeme, zda se text skutečně vygeneroval
                    final_snippet_html = f"<p>{plain_text}</p>" # Obklopíme do <p> pro jistotu, že Jinja2 detekuje neprázdný HTML fragment
            
                    logger.debug(f"BLOG Article: {article_key}. CHARS USED. Snippet length: {len(plain_text)}.")

            # 3d. Přidání do seznamu
            processed_articles.append({
                'title': cached_page.get('page', {}).get('title'),
                'url': article_meta.get('url'),
                'content_html': full_content_html,
                'snippet_html': final_snippet_html,
                'date': cached_page.get('page', {}).get('date', None),
            })
        else:
            logger.warning(f"BLOG: Could not load markdown for article: {article_key}")

    # 4. Příprava Jinja2 kontextu
    context = get_base_template_context(request, nav_builder)
    context.update({
        "page": page_data['page'],
        "articles": processed_articles,
        "pagination": {
            "current": current_page,
            "total": total_pages,
            "has_prev": current_page > 1,
            "has_next": current_page < total_pages,
            "prev_page": current_page - 1 if current_page > 1 else None,
            "next_page": current_page + 1 if current_page < total_pages else None,
            "base_url": f"/{page_slug}?" 
        },
        "blog_config": blog_config
    })
    
    # 5. Vykreslení
    return templates.TemplateResponse("blog_index.html.twig", context)
