# core/cache.py - Caching and Parsing Logic
import os
import yaml
import re
import logging
from pathlib import Path
from config import SITE_IDENTIFIKATOR
from core.utils import generate_clean_slug # Import new utility function # Import SITE_IDENTIFIKATOR

logger = logging.getLogger(__name__)

# --- Global Variables ---
PAGE_CACHE = {}
USER_ACCOUNTS_CACHE = {}
YAML_FRONTMATTER_REGEX = re.compile(r'^-{3,}\s*$(.*?)^\s*-{3,}', re.MULTILINE | re.DOTALL)

# --- Helper function for flattening dictionaries ---
def _flatten_dict_with_prefix(data, prefix="", separator="."):
    """
    Recursively flattens a nested dictionary, prepending keys with a given prefix.
    Example: _flatten_dict_with_prefix({'a': {'b': 1}}, prefix='_page') -> {'_page.a.b': 1}
    """
    flattened = {}
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        if isinstance(value, dict):
            flattened.update(_flatten_dict_with_prefix(value, new_key, separator))
        else:
            flattened[new_key] = value
    return flattened

# --- User Account Caching ---
def build_user_accounts_cache(directory="user/accounts"):
    """Loads all user accounts from YAML files into memory."""
    accounts_dir = Path(directory)
    if not accounts_dir.is_dir():
        logger.warning(f"User accounts directory not found: {accounts_dir}")
        return

    temp_accounts_cache = {}
    logger.info("Starting user accounts cache build...")
    for account_file in accounts_dir.glob('*.yaml'):
        try:
            username = account_file.stem
            account_data = yaml.safe_load(account_file.read_text(encoding='utf-8'))
            
            if account_data and "hashed_password" in account_data:
                account_data["hashed_password"] = account_data["hashed_password"].encode('utf-8')
                temp_accounts_cache[username] = account_data
                logger.debug(f"Loaded user account: {username}")
            else:
                logger.debug(f"Skipping invalid user account file: {account_file} (missing hashed_password or empty).")
        except Exception as e:
            logger.error(f"Error processing user account file {account_file}: {e}")
    
    USER_ACCOUNTS_CACHE.clear()
    USER_ACCOUNTS_CACHE.update(temp_accounts_cache)
    logger.info(f"User accounts cache build complete. Cached {len(USER_ACCOUNTS_CACHE)} accounts.")

# --- Page Content Parsing and Caching ---
def parse_frontmatter(content):
    """Parses a string to separate YAML frontmatter from Markdown content."""
    match = YAML_FRONTMATTER_REGEX.search(content)
    if match:
        frontmatter_str = match.group(1)
        content_str = content[match.end():]
        try:
            meta = yaml.safe_load(frontmatter_str) or {}
            logger.debug(f"Successfully parsed YAML frontmatter. Meta: {meta}")
            return meta, content_str.strip()
        except yaml.YAMLError as e:
            logger.warning(f"YAML parsing error in frontmatter: {e}. Content will be treated as plain Markdown.")
            return {}, content
    logger.debug("No YAML frontmatter found.")
    return {}, content

def _generate_slug_from_path(relative_path: Path) -> str:
    """Generates a URL-friendly slug from a file path, removing sorting prefixes."""
    cleaned_parts = []
    for part in relative_path.parts:
        if '.' in part and part.split('.', 1)[0].isdigit():
            cleaned_parts.append(part.split('.', 1)[1].lower())
        else:
            cleaned_parts.append(part.lower())
    return "/".join(cleaned_parts)

def build_page_cache(directory="user/pages"):
    """Loads all Markdown pages from the filesystem into memory, building hierarchical slugs."""
    pages_dir = os.environ.get('PAGES_DIR', directory)
    logger.debug(f"Attempting to build page cache from directory: {pages_dir}")
    base_dir = Path(pages_dir)
    if not base_dir.is_dir():
        logger.debug(f"Base directory not found: {base_dir}. Skipping page cache build.")
        return

    temp_cache = {}
    path_to_slug_map = {} # Helper to map physical paths to their slugs for parent lookups

    logger.info("Starting page cache build (Pass 1: Initial Parsing)...")
    # First pass: Parse all files and store their individual slugs
    all_md_files = sorted(list(base_dir.rglob('default.md')), key=lambda p: len(p.parts))

    for md_file in all_md_files:
        try:
            relative_dir_path = md_file.relative_to(base_dir).parent
            file_content = md_file.read_text(encoding='utf-8')
            page_meta, _ = parse_frontmatter(file_content)
            
            # Determine the slug for this specific level
            level_slug = page_meta.get('slug', generate_clean_slug(relative_dir_path.name))
            path_to_slug_map[relative_dir_path] = level_slug
        except Exception as e:
            logger.error(f"Error during initial parsing of {md_file}: {e}")

    logger.info("Starting page cache build (Pass 2: Hierarchical Slug Construction)...")
    for md_file in all_md_files:
        try:
            logger.debug(f"Processing file: {md_file}")
            absolute_file_path = str(md_file.resolve())
            relative_dir_path = md_file.relative_to(base_dir).parent

            if not relative_dir_path.parts:
                logger.debug(f"Skipping {md_file}: No relative directory path parts.")
                continue

            # Construct the hierarchical slug from the pre-parsed map
            slug_parts = []
            current_path = Path()
            for part in relative_dir_path.parts:
                current_path = current_path / part
                slug_part = path_to_slug_map.get(current_path)
                if slug_part:
                    slug_parts.append(slug_part)
                else:
                    # Fallback if a parent default.md was missing, though unlikely with this logic
                    slug_parts.append(generate_clean_slug(part))

            # CRITICAL: Ensure the final key is always lowercase for consistent lookups.
            final_cache_key_slug = "/".join(slug_parts).lower()
            
            file_content = md_file.read_text(encoding='utf-8')
            page_meta, md_content = parse_frontmatter(file_content)
            
            # A page should only be skipped if it has no content AND it's not a container or blog index.
            is_container = page_meta.get('container', False)
            is_blog_index = page_meta.get('blog', False)

            if not md_content.strip() and not is_container and not is_blog_index:
                logger.debug(f"Skipping {md_file}: Markdown content is empty, and it's neither a container nor a blog index.")
                continue

            logger.debug(f"Processing page {md_file}: final_cache_key_slug='{final_cache_key_slug}'")

            flattened_page_meta = _flatten_dict_with_prefix(page_meta, prefix="_page")
            
            page_entry = {
                "page": page_meta, 
                "markdown_content": md_content,
                "sort_key": relative_dir_path.parts[0], 
                "file_path": absolute_file_path,
                "slug": final_cache_key_slug,
                "slug_path": f"{SITE_IDENTIFIKATOR}/{final_cache_key_slug.lstrip('/')}".lower(),
                "title": page_meta.get('title', final_cache_key_slug.split('/')[-1].replace('-', ' ').capitalize()),
                "path_parts": list(relative_dir_path.parts)
            }
            page_entry.update(flattened_page_meta)
            temp_cache[final_cache_key_slug] = page_entry
            logger.debug(f"Cached page '{final_cache_key_slug}' from {md_file}.")

        except Exception as e:
            logger.error(f"Error processing file {md_file} in second pass: {e}")
    
    PAGE_CACHE.clear()
    PAGE_CACHE.update(temp_cache)
    logger.debug(f"Final PAGE_CACHE content: {PAGE_CACHE}")
    logger.info(f"Page cache build complete. Cached {len(PAGE_CACHE)} pages.")
