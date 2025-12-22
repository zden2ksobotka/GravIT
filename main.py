import os
import yaml
import logging
import bcrypt
import sys
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from watchdog.observers import Observer
from pathlib import Path
import json
from urllib.parse import urlparse

# --- Project-Specific Imports ---
from config import THEME_SKIN, DEBUG, SECRET_KEY, LOG_LEVEL
from core.navigation import NavigationBuilder
from core.file_watcher import start_watcher

# --- Core Module Imports ---
from core.cache import PAGE_CACHE, USER_ACCOUNTS_CACHE, build_page_cache, build_user_accounts_cache, _generate_slug_from_path
from core.plugins import load_plugins
from core.security import AuthManager, get_current_user, get_page_access_by_spec_rules
from core.templating import templates, get_base_template_context, THEME_CONFIG
from core.content import get_page_data
from core.utils import generate_clean_slug, remove_diacritics, render_html_list, render_multicolumn_list, parse_container_config, wrap_in_container_div
try:
    from user.plugin.blog.blog import blog_page_handler # NOVÝ IMPORT
except ModuleNotFoundError:
    blog_page_handler = None

# --- Logger Setup ---
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    "DISABLED": logging.CRITICAL + 1  # Effectively disables logging
}

# Determine the effective log level based on LOG_LEVEL setting
effective_log_level = LOG_LEVEL_MAP.get(LOG_LEVEL.upper(), logging.INFO)

os.makedirs('log', exist_ok=True)

# Create a root logger
root_logger = logging.getLogger()
root_logger.setLevel(effective_log_level)

# Clear existing handlers to prevent duplicate output if reloaded
if root_logger.handlers:
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

# File handler
file_handler = logging.FileHandler('log/debug.log', mode='a')
file_handler.setLevel(effective_log_level)
file_formatter = logging.Formatter('%(asctime)s - %(process)d - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(effective_log_level)
console_formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)

# Apply the effective log level to specific loggers
logging.getLogger('core.navigation').setLevel(effective_log_level)
logging.getLogger('watchdog').setLevel(effective_log_level)
logging.getLogger('core.file_watcher').setLevel(effective_log_level) # Ensure file_watcher also respects the setting

# Get specific logger for this module
logger = logging.getLogger(__name__)
logger.debug("main.py started.")

# --- Global Variables ---
observer: Observer = None

# --- Initial Content and Navigation Build (Run in Global Scope for Multi-Worker Safety) ---
logging.info("Building initial caches in global scope...")
build_user_accounts_cache()
build_page_cache()
nav_builder = NavigationBuilder(PAGE_CACHE, get_page_access_by_spec_rules)
logging.info("Initial NavigationBuilder created.")

# --- FastAPI Application Initialization ---
app = FastAPI()

# Load theme config early for plugins
theme_config_path = Path(f"{THEME_SKIN}/theme.yaml")
if theme_config_path.exists():
    THEME_CONFIG.update(yaml.safe_load(theme_config_path.read_text()))
    logger.debug(f"Theme configuration loaded from {theme_config_path}.")
else:
    logger.warning(f"Theme configuration file not found at {theme_config_path}. Using default settings.")

# Load plugins right after app initialization
logger.info("Calling load_plugins...")
load_plugins(
    app,
    get_nav_builder=lambda: nav_builder,
    templates=templates,
    theme_config=THEME_CONFIG,
    theme_skin=THEME_SKIN,
    get_full_page_cache=lambda: PAGE_CACHE # Added for new author and dumpcache plugins
)



# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Mount static file directories
app.mount("/user/theme", StaticFiles(directory="user/theme"), name="themes")
app.mount("/user/pages", StaticFiles(directory="user/pages"), name="user_pages")
app.mount("/user/accounts", StaticFiles(directory="user/accounts"), name="user_accounts")
app.mount("/user/plugin", StaticFiles(directory="user/plugin"), name="plugins")


# --- Live Reload and Application Lifecycle ---
def reload_all_content():
    """Central function to reload all caches and rebuild navigation."""
    global nav_builder
    logger.info("--- RELOADING ALL CONTENT ---")
    try:
        theme_config_path = Path(f"{THEME_SKIN}/theme.yaml")
        if theme_config_path.exists():
            THEME_CONFIG.clear()
            THEME_CONFIG.update(yaml.safe_load(theme_config_path.read_text()))
            logger.info("Theme configuration reloaded.")
        else:
            logger.warning(f"Theme configuration file not found at {theme_config_path} during reload. Using existing settings.")

        build_user_accounts_cache()
        build_page_cache()

        nav_builder = NavigationBuilder(PAGE_CACHE, get_page_access_by_spec_rules)
        logger.info("NavigationBuilder rebuilt.")
        logger.info("--- CONTENT RELOAD COMPLETE ---")
    except Exception as e:
        logger.error(f"Error during content reload: {e}", exc_info=True)

@app.on_event("startup")
async def startup_event():
    global observer
    logger.info("FastAPI application startup event initiated.")
    paths_to_watch = ["user/pages", "user/accounts", f"{THEME_SKIN}/theme.yaml"]
    observer = start_watcher(paths_to_watch, reload_all_content)
    logger.info("File watcher initialized and started.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI application shutdown event initiated.")
    if observer:
        observer.stop()
        observer.join()
        logger.info("File watcher stopped.")
    logger.info("FastAPI application shutdown complete.")


# --- Authentication Routes ---
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request, message: str = None, next: str = None, access_denied: bool = False, from_page: str = None):
    logger.debug(f"Accessing login page. Message: {message}, Next URL: {next}, Access Denied: {access_denied}, From Page: {from_page}")
    
    # If from_page is not provided by an access-denied redirect, try to get it from the Referer header.
    if not from_page:
        referer_url = request.headers.get("referer")
        if referer_url:
            parsed_referer = urlparse(referer_url)
            # Make sure the referer is not the login page itself and is from the same host
            if parsed_referer.path != "/login" and parsed_referer.hostname == request.url.hostname:
                from_page = parsed_referer.path
                if parsed_referer.query:
                    from_page += f"?{parsed_referer.query}"

    # Redirect a logged-in user away, ONLY if they didn't land here due to an "access denied" error.
    if get_current_user(request) and not access_denied:
        logger.info("User already logged in and not facing an access error, redirecting from login page to /.")
        return RedirectResponse(url="/", status_code=303)
    
    context = get_base_template_context(request, nav_builder)
    context.update({
        "message": message,
        "page": {"title": "Login", "hero": {"enabled": False}, "sidebar": {"enabled": False, "widgets": []}, "breadcrumbs": [{"title": "Login", "url": "/login"}]},
        "content": "",
        "next_url": next,
        "from_page": from_page,  # Pass the determined from_page URL to the template
    })
    logger.debug("Rendering login.html.twig")
    return templates.TemplateResponse("login.html.twig", context)

@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...), next_url: str = Form("/")):
    logger.debug(f"Attempting login for username: {username}, next_url: {next_url}")
    user_account = USER_ACCOUNTS_CACHE.get(username)
    error_message = "Invalid credentials or account disabled."

    if not user_account:
        logger.warning(f"Login failed for username '{username}': User account not found.")
        return RedirectResponse(url=f"/login?message={error_message}&next={next_url}", status_code=303)
    
    # Robust, case-insensitive check for user state.
    # Only allows login if state is explicitly 'enabled' or 'true'.
    # Defaults to 'disabled' if key is missing for safety.
    user_state = str(user_account.get("state", "disabled")).lower()
    if user_state not in ["enabled", "true"]:
        logger.warning(f"Login failed for username '{username}': Account is disabled (state: '{user_state}').")
        return RedirectResponse(url=f"/login?message={error_message}&next={next_url}", status_code=303)

    hashed_password = user_account.get("hashed_password")
    if not hashed_password or not bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        logger.warning(f"Login failed for username '{username}': Invalid password.")
        return RedirectResponse(url=f"/login?message={error_message}&next={next_url}", status_code=303)

    request.session["username"] = username
    request.session["login_time"] = datetime.now().isoformat()
    logger.info(f"User '{username}' successfully logged in.")
    
    if next_url and (next_url.startswith("/") and not next_url.startswith("//")):
        logger.debug(f"Redirecting user '{username}' to next_url: {next_url}")
        return RedirectResponse(url=next_url, status_code=303)
    logger.debug(f"Redirecting user '{username}' to root after login.")
    return RedirectResponse(url="/", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    current_user = get_current_user(request)
    username = current_user.get('username') if current_user else 'anonymous'
    next_url = request.query_params.get("next")

    request.session.pop("username", None)
    request.session.pop("login_time", None)
    logger.info(f"User '{username}' logged out.")

    if next_url:
        # Redirect to the login page, preserving the original destination
        return RedirectResponse(url=f"/login?next={next_url}", status_code=303)
    
    # Default redirect to home page if no next_url is specified
    return RedirectResponse(url="/", status_code=303)


# --- User Profile Route ---
@app.get("/profile", response_class=HTMLResponse)
async def user_profile(request: Request):
    logger.debug("Accessing user profile page.")
    current_user = get_current_user(request)
    if not current_user:
        logger.info("Attempt to access profile page by unauthenticated user, redirecting to login.")
        return RedirectResponse(url="/login?next=/profile", status_code=303)

    login_time_str = request.session.get("login_time")
    login_time = datetime.fromisoformat(login_time_str) if login_time_str else None
    session_duration = timedelta(days=14)
    expires_time = login_time + session_duration if login_time else None
    time_left = expires_time - datetime.now() if expires_time else None
    time_left_parts = None
    if time_left:
        days, remainder = time_left.days, time_left.seconds
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        time_left_parts = {"days": days, "hours": hours, "minutes": minutes}

    context = get_base_template_context(request, nav_builder)
    context.update({
        "login_time": login_time,
        "expires_time": expires_time,
        "time_left_parts": time_left_parts,
        "page": {"title": "User Profile", "hero": {"enabled": False}, "sidebar": {"enabled": False, "widgets": []}, "breadcrumbs": [{"title": "User Profile", "url": "/profile"}]},
    })
    logger.debug(f"Rendering profile page for user: {current_user.get('username')}")
    return templates.TemplateResponse("profile.html.twig", context)


# --- Main Content Route ---
@app.get("/{page_path:path}", response_class=HTMLResponse)
async def read_page(request: Request, page_path: str):
    logger.debug(f"Request to read page for path: '{page_path}'")
    page_path_from_url = page_path.lower() if page_path else sorted(PAGE_CACHE.items(), key=lambda item: item[1]['sort_key'])[0][0].lower()
    page_path_to_load = page_path_from_url
    logger.debug(f"Resolved page_path_to_load: '{page_path_to_load}'")

    # --- Refactored Access Control ---
    auth_manager = AuthManager()
    access_response = auth_manager.check_access_and_get_response(request, page_path_to_load)
    if access_response:
        return access_response  # Immediately return the redirect if access is denied

    # Initialize container variables to avoid UnboundLocalError
    is_container = False
    num_columns = 1
    list_format = 'list2'
    show_all_children = True
    
    if access_response:
        return access_response  # Immediately return the redirect if access is denied

    # Initialize container variables to avoid UnboundLocalError
    is_container = False
    num_columns = 1
    list_format = 'list2'
    show_all_children = True
    
    # Re-define current_user as it's needed for other parts of the function (e.g., get_children_details)
    current_user = get_current_user(request)
    username_log = current_user.get('username') if current_user else 'anonymous'
    logger.debug(f"Access granted for page '{page_path_to_load}' for user '{username_log}'. Proceeding with content retrieval.")
    
    # --- NEW CONTAINER-FIRST LOGIC (Refactored) ---
    cached_page = PAGE_CACHE.get(page_path_to_load, {})
    page_meta = cached_page.get('page', {})
    current_user_is_logged_in = bool(current_user)
    
    # --- BLOG INDEX CHECK (High Priority) ---
    if page_meta.get('blog', False) and blog_page_handler:
        logger.info(f"Page '{page_path_to_load}' is a blog index. Handing off to blog_page_handler.")
        return await blog_page_handler(
            request, 
            cached_page, 
            page_path_to_load, 
            page_path,
            get_nav_builder=lambda: nav_builder,
            get_full_page_cache=lambda: PAGE_CACHE
        )
    
    is_container, num_columns, list_format, show_all_children = parse_container_config(page_meta, current_user_is_logged_in)


    data = None
    if is_container:
        logger.info(f"Page '{page_path_to_load}' is a container. Format: {list_format}, Columns: {num_columns}.")
        
        # <<< TEMPORARY DEBUG LOGGING >>>
        logger.debug(f"DEBUG: num_columns = {num_columns} (type: {type(num_columns)})")

        children_json_list = nav_builder.get_children_details(page_path_to_load, current_user, show_all_children=show_all_children)
        children_data = [json.loads(s) for s in children_json_list]
        
        html_content = render_multicolumn_list(children_data, num_columns, format=list_format)

        index_title = page_meta.get('title', page_path_to_load.split('/')[-1].replace('-', ' ').capitalize())
        data = {"page": {"title": f"Index of {index_title}"}, "content": html_content}
    else:
        # If not an explicit container, try to get page data. It might be a regular page or a directory without default.md
        logger.debug(f"Page '{page_path_to_load}' is not an explicit container. Attempting to retrieve standard page data.")
        data = get_page_data(page_path_to_load)

    # Fallback: if no data yet (e.g. dir without default.md), try to generate an index.
        if not data:
            logger.debug(f"No direct page data for '{page_path_to_load}'. Attempting to generate index of subpages as a fallback.")
            children_json_list = nav_builder.get_children_details(page_path_to_load, current_user, show_all_children=show_all_children)
            children_data = [json.loads(s) for s in children_json_list]
    
            if children_data:
                html_content = render_html_list(children_data, tag='ol', css_class='index-list')
                html_content = wrap_in_container_div(html_content)
                index_title = page_path_to_load.split('/')[-1].replace('-', ' ').capitalize() if page_path_to_load else "Root"
                data = {"page": {"title": f"Index of {index_title}"}, "content": html_content}
                logger.info(f"Generated index page for '{page_path_to_load}'. Title: '{index_title}'")
        
        if not data:
            logger.error(f"Page '{page_path_to_load}' not found and no index could be generated. Raising 404 HTTPException.")
            raise HTTPException(status_code=404, detail=f"Page '{page_path_to_load}' not found.")
    if data is None:
        logger.error(f"Failed to retrieve or generate content for page path '{page_path_to_load}'. Aborting page rendering.")
        raise HTTPException(status_code=404, detail=f"Page '{page_path_to_load}' not found.")

    # Add slug to page data so it's available in the template context.
    # This is required for plugins like 'page-yaml' to function correctly.
    data['page']['slug'] = page_path_to_load
    logger.debug(f"Added slug '{page_path_to_load}' to page data.")
    
    # Breadcrumb Generation (Refactored)
    breadcrumbs = nav_builder.generate_breadcrumbs(page_path, data)
    data['page']['breadcrumbs'] = breadcrumbs
    logger.debug(f"Generated breadcrumbs: {breadcrumbs}")

    context = get_base_template_context(request, nav_builder)
    context.update(data)
    logger.debug("Base template context updated.")
    
    template_name = data.get("page", {}).get("template", "base.html.twig") or "base.html.twig"
    logger.debug(f"Rendering page using template: '{template_name}' for page_path: '{page_path_to_load}'.")
    return templates.TemplateResponse(template_name, context)
