import re
import logging
from fastapi import Request
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
from bs4 import BeautifulSoup  # Import BeautifulSoup
from user.plugin.search.search_config import (
    SEARCH_RESULTS_COUNT, 
    SEARCH_RELEVANT_RESULTS, 
    MIN_SEARCH_LENGTH,
    PAGE_TREE_ENABLED,
    PAGE_TREE_TITLE,
    PAGE_TREE_ALL_VISIBLE,
    SNIPPET_PRE_LENGTH,
    SNIPPET_POST_LENGTH
)

logger = logging.getLogger(__name__)


def _get_word_aware_snippet(text: str, start: int, end: int, query: str) -> str:
    """
    Generates a word-aware snippet around the matched term.
    """
    text_length = len(text)
    
    # Calculate desired snippet boundaries
    snippet_start = max(0, start - SNIPPET_PRE_LENGTH)
    snippet_end = min(text_length, end + SNIPPET_POST_LENGTH)

    # Adjust start to the nearest word boundary
    while snippet_start > 0 and text[snippet_start - 1].isalnum():
        snippet_start -= 1
    
    # Adjust end to the nearest word boundary
    while snippet_end < text_length and text[snippet_end].isalnum():
        snippet_end += 1

    snippet = text[snippet_start:snippet_end]
    
    # Highlight the query within the snippet
    # Using re.sub with a lambda to handle potential multiple matches and case-insensitivity
    highlighted_snippet = re.sub(
        re.escape(query),
        lambda match: f"<mark>{match.group(0)}</mark>",
        snippet,
        flags=re.IGNORECASE
    )
    
    return highlighted_snippet


def register_routes(app, templates, theme_config, cms_theme, get_nav_builder, get_active_plugins, get_full_page_cache):

    @app.get("/search/config")
    async def search_config():
        """
        Returns search configuration to the frontend.
        """
        return {"min_length": MIN_SEARCH_LENGTH}

    @app.get("/search")
    async def search_pages(request: Request, q: str = ""):
        logger.info(f"--- Search request received for query: '{q}' ---")
        
        # --- Branch 1: Show Page Tree (if enabled and query is empty/short) ---
        if PAGE_TREE_ENABLED and (not q or len(q.strip()) < MIN_SEARCH_LENGTH):
            logger.info("Query is empty or too short, and tree view is enabled. Displaying page tree.")
            
            # Need to get current_user to pass to the builder
            from main import get_current_user
            current_user = get_current_user(request)

            nav_builder = get_nav_builder()
            page_tree_html = nav_builder.get_search_tree_html(
                current_user=current_user, 
                show_all=PAGE_TREE_ALL_VISIBLE
            ) if nav_builder else ""
            
            context = {
                "request": request,
                "is_tree_view": True,
                "tree_title": PAGE_TREE_TITLE,
                "page_tree_html": Markup(page_tree_html),
                "query_message": "",
                "active_plugin_names": get_active_plugins()
            }
            return templates.TemplateResponse("partials/search-results.html.twig", context)

        # --- Handle short/empty query when tree is disabled ---
        if not q or len(q.strip()) < MIN_SEARCH_LENGTH:
            logger.info(f"Query '{q}' is too short and tree view is disabled. Returning empty results.")
            context = {
                "request": request,
                "is_tree_view": False,
                "search_query": q,
                "search_results": [],
                "query_message": f"Enter at least {MIN_SEARCH_LENGTH} characters to start searching.",
                "active_plugin_names": get_active_plugins()
            }
            return templates.TemplateResponse("partials/search-results.html.twig", context)

        # --- Branch 2: Perform Standard Search ---
        try:
            page_cache = get_full_page_cache()
            all_page_matches = []
            search_pattern = re.compile(q, re.IGNORECASE)
            
            for slug, page_data in page_cache.items():
                html_content = page_data.get("markdown_content", "")
                if not html_content: continue

                # Use BeautifulSoup to get clean, searchable text from the HTML content.
                soup = BeautifulSoup(html_content, "html.parser")
                clean_text = soup.get_text()

                page_title = page_data['page'].get("title", slug.capitalize())
                # Perform the search on the clean text, not the raw HTML.
                matches = list(search_pattern.finditer(clean_text))
                
                if matches:
                    all_page_matches.append({
                        "slug": slug, "title": page_title,
                        "matches": matches,
                        "clean_content": clean_text  # Pass the clean text for snippet generation
                    })

            all_page_matches.sort(key=lambda x: len(x["matches"]), reverse=True)
            all_page_matches = all_page_matches[:SEARCH_RELEVANT_RESULTS]

            search_results = []
            for page_match_data in all_page_matches:
                snippets = []
                processed_snippet_areas = []
                for match in page_match_data["matches"]:
                    if len(snippets) >= SEARCH_RESULTS_COUNT:
                        break

                    start, end = match.span()

                    is_overlapping = False
                    # Check for overlapping snippets based on match area to avoid redundant snippets
                    # We are only checking if the *match itself* overlaps with a *previously processed snippet area*.
                    # This is not checking if the *new snippet area* overlaps with *previous snippet areas*.
                    # The purpose is to ensure that each match contributes to a snippet only once,
                    # and that we don't generate snippets for matches that fall entirely within
                    # an already covered snippet.
                    for proc_start, proc_end in processed_snippet_areas:
                        # Check if the current match's span (start, end) overlaps with
                        # any of the previously processed snippet areas.
                        if max(start, proc_start) < min(end, proc_end):
                            is_overlapping = True
                            break
                    
                    if is_overlapping:
                        continue

                    # Generate the word-aware snippet
                    highlighted_snippet = _get_word_aware_snippet(
                        page_match_data["clean_content"], start, end, q
                    )
                    snippets.append(Markup(highlighted_snippet))
                    
                    # Store the *actual* start and end of the generated snippet for overlap checking
                    # This ensures that subsequent matches don't generate snippets that significantly overlap
                    # with the current one, even if the match itself is not fully contained.
                    cleaned_snippet = re.sub(r'<[^>]+>', '', highlighted_snippet)
                    snippet_start_actual = page_match_data["clean_content"].find(cleaned_snippet)
                    if snippet_start_actual != -1:
                        snippet_end_actual = snippet_start_actual + len(cleaned_snippet)
                        processed_snippet_areas.append((snippet_start_actual, snippet_end_actual))
                
                if snippets:
                    search_results.append({
                        "slug": page_match_data["slug"], "title": page_match_data["title"],
                        "snippets": snippets
                    })

            context = {
                "request": request, "search_query": q,
                "search_results": search_results,
                "query_message": "No results were found." if not search_results else "",
                "page": {"title": f"Search results for '{q}'"},
                "theme": theme_config, "theme_path": cms_theme,
                "active_plugin_names": get_active_plugins()
            }
            
            return templates.TemplateResponse("partials/search-results.html.twig", context)

        except Exception as e:
            logger.error(f"--- CRITICAL ERROR during search for query '{q}': {e} ---", exc_info=True)
            return templates.TemplateResponse("partials/search-results.html.twig", {
                "request": request, "search_results": [], 
                "query_message": "An internal error occurred while processing your query.",
                "active_plugin_names": get_active_plugins()
            })
