# core/security.py - Access Control and Authentication Logic
from fastapi import Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Global caches will be imported from core.cache
from core.cache import PAGE_CACHE, USER_ACCOUNTS_CACHE

class AuthManager:
    """Handles authorization and access control logic."""

    def check_access_and_get_response(self, request: Request, page_path_to_load: str) -> RedirectResponse | None:
        """
        Checks if the current user can access a page.
        Returns a RedirectResponse if access is denied, otherwise returns None.
        """
        current_user = get_current_user(request)
        username_log = current_user.get('username') if current_user else 'anonymous'
        logger.debug(f"AuthManager: Checking access for page '{page_path_to_load}' for user '{username_log}'.")

        can_access = get_page_access_by_spec_rules(page_path_to_load, current_user)
        if can_access:
            logger.debug(f"AuthManager: Access GRANTED for '{page_path_to_load}'.")
            return None  # Access granted, no response needed.

        # --- Access is DENIED from this point on ---
        logger.warning(f"AuthManager: Access DENIED for '{page_path_to_load}' for user '{username_log}'.")
        
        # Determine the 'from_page' URL from the Referer header for the BACK button
        referer_url = request.headers.get("referer")
        from_page_url = "/"  # Default fallback

        if referer_url:
            parsed_referer = urlparse(referer_url)
            if parsed_referer.hostname == request.url.hostname:
                from_page_url = parsed_referer.path
                if parsed_referer.query:
                    from_page_url += f"?{parsed_referer.query}"
            else:
                logger.warning(f"External referer '{referer_url}', falling back to '/' for security.")
        else:
            logger.debug("No referer header found, falling back to '/'.")

        # If user is NOT logged in, redirect to login page.
        if not current_user:
            logger.info(f"Unauthenticated user denied. Redirecting to login for '{page_path_to_load}'.")
            return RedirectResponse(url=f"/login?next=/{page_path_to_load}&from_page={from_page_url}", status_code=303)
        
        # If user IS logged in but lacks permissions, redirect to login with a specific message.
        else:
            logger.info(f"Authenticated user '{username_log}' denied. Redirecting to login with 'access_denied' message.")
            message = f"Access to the page '{page_path_to_load}' is denied. Your account lacks the required permissions."
            return RedirectResponse(url=f"/login?message={message}&access_denied=true&next=/{page_path_to_load}&from_page={from_page_url}", status_code=303)


def get_page_meta(slug: str, key_path: str, default=None):
    """Safely retrieves a nested value from a page's metadata."""
    logger.debug(f"get_page_meta: Retrieving meta for slug='{slug}', key_path='{key_path}'")
    try:
        if slug not in PAGE_CACHE:
            logger.debug(f"get_page_meta: Slug '{slug}' not found in PAGE_CACHE. Returning default.")
            return default
        page_data = PAGE_CACHE[slug].get('page', {})
        
        keys = key_path.split('.')
        current_level = page_data
        for key in keys:
            current_level = current_level.get(key) if isinstance(current_level, dict) else default
            if current_level is None:
                logger.debug(f"get_page_meta: Key path part '{key}' not found for slug='{slug}'. Returning default.")
                return default
        logger.debug(f"get_page_meta: Successfully retrieved '{key_path}' for slug='{slug}'. Value: {current_level}")
        return current_level
    except Exception as e:
        logger.error(f"Error retrieving page meta for slug='{slug}', key_path='{key_path}': {e}", exc_info=True)
        return default

def get_page_access_by_spec_rules(page_identifier, current_user: dict = None) -> bool:
    """Centralized function to check all access rules for a given page and user."""
    
    if isinstance(page_identifier, str):
        slug_for_logging = page_identifier
        page_access_rules = get_page_meta(page_identifier, 'access', {})
    elif isinstance(page_identifier, dict):
        slug_for_logging = "ACCESS_RULES_DICT"
        page_access_rules = page_identifier
    else:
        # Invalid type, deny access for safety
        slug_for_logging = "INVALID_IDENTIFIER"
        page_access_rules = {}

    logger.debug(f"get_page_access_by_spec_rules: Checking access for identifier='{slug_for_logging}', user='{current_user.get('username') if current_user else 'anonymous'}'")

    if not page_access_rules:
        logger.debug(f"get_page_access_by_spec_rules: No specific access rules for page '{slug_for_logging}'. Access granted by default.")
        return True

    user_permissions = current_user.get('access', {}) if current_user else {}
    if not user_permissions and current_user:
        logger.warning(f"get_page_access_by_spec_rules: User '{current_user.get('username')}' has no defined permissions but is authenticated.")

    # Check for negative rules first (e.g., access: site.login: false)
    for perm_key, required_value in page_access_rules.items():
        if required_value is False:
            perm_parts = perm_key.split('.')
            current_level = user_permissions
            for part in perm_parts:
                current_level = current_level.get(part) if isinstance(current_level, dict) else None
                if current_level is None: break
            
            if current_level is True:
                logger.debug(f"get_page_access_by_spec_rules: Access DENIED for page '{slug_for_logging}' due to negative rule '{perm_key}'.")
                return False # Negative rule is an immediate exit

    # Now check for positive rules (e.g., access: site.login: true)
    required_true_rules = {k: v for k, v in page_access_rules.items() if v is True}

    if not required_true_rules:
        logger.debug(f"get_page_access_by_spec_rules: No positive access rules for page '{slug_for_logging}'. Access granted by default.")
        return True

    # If we have positive rules, access is denied by default unless a rule is met.
    access_granted = False
    if current_user:
        for perm_key, required_value in required_true_rules.items():
            perm_parts = perm_key.split('.')
            current_level = user_permissions
            for part in perm_parts:
                current_level = current_level.get(part) if isinstance(current_level, dict) else None
                if current_level is None: break
            
            if current_level is True:
                access_granted = True
                logger.debug(f"get_page_access_by_spec_rules: Access GRANTED for page '{slug_for_logging}' by rule '{perm_key}'.")
                break # First matching rule is enough
    
    if not access_granted:
        logger.debug(f"get_page_access_by_spec_rules: Access DENIED for page '{slug_for_logging}' - no matching positive rule found for user.")

    logger.debug(f"get_page_access_by_spec_rules: Final access decision for page '{slug_for_logging}': {access_granted}.")
    return access_granted

def get_current_user(request: Request):
    """Retrieves the current user's data from the session cookie."""
    username = request.session.get("username")
    logger.debug(f"get_current_user: Attempting to retrieve user from session. Username in session: {username}")
    if username and username in USER_ACCOUNTS_CACHE:
        logger.debug(f"get_current_user: User '{username}' found in cache.")
        return USER_ACCOUNTS_CACHE[username]
    logger.debug(f"get_current_user: User '{username}' not found in cache or not in session.")
    return None
