# navigation_builder.py - Centralized Navigation Logic
# This module provides a single class, NavigationBuilder, responsible for creating all
# navigation structures, including the main menu and the full sitemap (page tree).

import logging
import json
import re
from config import SITE_IDENTIFIKATOR
from core.utils import generate_clean_slug, render_html_list, remove_diacritics # Import new utility functions

# Get a logger instance for this module.
logger = logging.getLogger(__name__)

# IMPORTANT! This class is the single source of truth for navigation.
# By centralizing the logic here, we ensure that the main menu and the sitemap
# are always consistent in structure, sorting, and access control. It takes the raw
# page data and transforms it into a hierarchical tree.
class NavigationBuilder:
    """
    Builds and manages hierarchical navigation structures from a flat page cache.
    """
    def __init__(self, page_cache, access_checker):
        """
        Initializes the NavigationBuilder.
        Args:
            page_cache (dict): The global PAGE_CACHE containing all page data.
            access_checker (function): A reference to the get_page_access_by_spec_rules function from main.py.
                                       This is a key dependency for checking permissions.
        """
        self.page_cache = page_cache
        self.access_checker = access_checker
        self.site_identifier = SITE_IDENTIFIKATOR # Store the site identifier
        self.parent_to_children_map = {} # OPTIMIZATION: Direct lookup map
        # IMPORTANT! The tree is built only once upon initialization.
        # This is efficient as it avoids rebuilding the entire structure on every request.
        # The tree is rebuilt only when the application reloads its content.
        self.tree = self._build_tree()

    def _build_tree(self):
        """
        Constructs a hierarchical tree and a parent-to-children map from the flat PAGE_CACHE.
        """
        tree = {self.site_identifier: {'__meta__': {}, '__children__': {}}}
        # Reset the map each time the tree is built
        self.parent_to_children_map = {self.site_identifier: []}

        sorted_pages = sorted(self.page_cache.items(), key=lambda item: len(item[0].split('/')))
        
        for slug, page_data in sorted_pages:
            parts = page_data.get('path_parts', slug.split('/'))
            if not parts:
                continue

            # --- Populate parent_to_children_map ---
            parent_slug = '/'.join(slug.split('/')[:-1]) if '/' in slug else self.site_identifier
            if parent_slug not in self.parent_to_children_map:
                self.parent_to_children_map[parent_slug] = []
            self.parent_to_children_map[parent_slug].append(slug)
            
            # --- Build the hierarchical tree ---
            current_level = tree[self.site_identifier]['__children__']
            for part in parts[:-1]:
                node = current_level.setdefault(part, {'__meta__': {}, '__children__': {}})
                current_level = node['__children__']
            
            last_part = parts[-1]
            page_node = current_level.setdefault(last_part, {'__meta__': {}, '__children__': {}})
            page_node['__meta__'] = page_data
            
        logger.debug(f"Parent-to-children map successfully built: {json.dumps(self.parent_to_children_map, indent=2)}")
        logger.debug("_build_tree: Finished building navigation tree.")
        return tree

    def _get_sort_key(self, item: tuple) -> tuple:
        """
        Helper function to determine the sort key for a navigation item.
        It prioritizes numeric prefixes (e.g., '01.', '5.') for sorting.
        """
        original_part, _ = item
        match = re.match(r'^(\d+)\.', original_part)
        if match:
            # If a numeric prefix is found, use its integer value for sorting.
            return (0, int(match.group(1)))
        # Otherwise, sort alphabetically after numbered items.
        return (1, original_part)

    def _build_navigation_data(self, tree_node: dict, current_user: dict, for_main_nav: bool, parent_slug: str = ""):
        """
        The core recursive method. Builds a nested list of navigation items.
        It traverses the internal tree, applies access and visibility rules,
        and generates clean slugs for URLs.
        
        Args:
            tree_node (dict): The current node of the tree to process.
            current_user (dict): The currently logged-in user, or None.
            for_main_nav (bool): If True, respects the 'visible: false' rule. If False, includes all accessible items (for sitemap).
            parent_slug (str): The URL slug of the parent item, used to build nested URLs.
        """
        items = []

        # Helper function to sort items based on their numeric prefix (e.g., '01.').
        sorted_tree_items = sorted(tree_node.items(), key=self._get_sort_key)

        for original_part, branch in sorted_tree_items:
            # Add comprehensive logging at the start of each item's processing
            logger.debug(f"DEBUG_NAV: Enter -> parent_slug='{parent_slug}', original_part='{original_part}'")

            meta = branch.get('__meta__', {})
            children = branch.get('__children__', {})

            # --- Slug Generation ---
            # Creates a clean URL part from the original directory name.
            # e.g., "01.About" becomes "about".
            cleaned_part = generate_clean_slug(original_part)
            
            # Determine the effective slug for the current item's *segment*, prioritizing frontmatter slug.
            frontmatter_raw_slug = meta.get('page', {}).get('slug')
            if frontmatter_raw_slug:
                # If frontmatter slug is present, use its last segment (e.g., "linux/acmesh" -> "acmesh")
                effective_item_slug_segment = frontmatter_raw_slug.split('/')[-1].lower()
            else:
                # If no frontmatter slug, use the cleaned directory name (already lowercase)
                effective_item_slug_segment = cleaned_part

            # Construct the full URL-like path for the current item.
            # This should be built by combining the parent_slug with the current item's single-segment slug.
            if parent_slug and parent_slug != self.site_identifier:
                item_full_slug_path = f"{parent_slug}/{effective_item_slug_segment}"
            else:
                item_full_slug_path = effective_item_slug_segment # Top-level item or directly under site_identifier
            
            # Log the key slugs and paths
            logger.debug(f"DEBUG_NAV: Slugs -> cleaned_part='{cleaned_part}', frontmatter_slug='{meta.get('page', {}).get('slug')}', effective_item_slug_segment='{effective_item_slug_segment}', item_full_slug_path='{item_full_slug_path}'")



            # --- CRITICAL LOGIC: VISIBILITY ---
            # Visibility is a rendering concern and therefore belongs here.
            # This block checks the 'visible' flag directly from the page's metadata.
            # This is the ONLY place that should prevent an item from appearing in the main menu.
            if for_main_nav and meta.get('page', {}).get('visible') is False:
                logger.debug(f"Skipping '{item_full_slug_path}' from main nav because visible is false.")
                continue

            # Determine the display title for the navigation item.
            # Priority: 1. Title from frontmatter, 2. Cleaned directory name.
            title = meta.get('page', {}).get('title')
            if not title:
                # Clean the original_part for display purposes (remove numeric prefix and replace hyphens).
                display_name = original_part
                if '.' in original_part and original_part.split('.', 1)[0].isdigit():
                    display_name = original_part.split('.', 1)[1]
                title = display_name.replace('-', ' ').capitalize()
            
            # Create the navigation item dictionary.
            # If the item is directly under the site_identifier, its URL should start with '/'
            if parent_slug == self.site_identifier or not parent_slug:
                nav_url = f"/{item_full_slug_path}"
            else:
                nav_url = f"/{item_full_slug_path}"
            
            is_container = meta.get('page', {}).get('container', False) is True
            
            # A container should always be clickable, pointing to its own index page.
            # The URL is correctly generated as nav_url from the slug.
            nav_item = {
                "title": title,
                "url": nav_url,
                "is_container": is_container,
                "path_slug": cleaned_part, # Keep track of path-based slug (lowercase)
                "frontmatter_slug": meta.get('page', {}).get('slug'), # Slug from frontmatter (original casing)
                "children": [],
                "has_children": bool(children)
            }

            # If the item has children, recursively build their navigation data.
            if children:
                # Pass the full constructed slug path of the current item as the parent_slug (lowercase)
                # for its children.
                nav_item["children"] = self._build_navigation_data(children, current_user, for_main_nav, parent_slug=item_full_slug_path)
            
            logger.debug(f"DEBUG_NAV: Appending nav_item -> {json.dumps(nav_item, indent=2)}")
            items.append(nav_item)
        
        return items

    # --- Public Methods ---

    def get_menu_data(self, current_user: dict):
        """
        Returns the data structure for the main menu.
        This method respects the 'visible: false' flag in page frontmatter.
        The output is a list of dictionaries, intended for rendering in a Jinja2 template.
        """
        # Pass self.site_identifier as the initial parent_slug to start building from the root
        return self._build_navigation_data(self.tree[self.site_identifier]['__children__'], current_user, for_main_nav=True, parent_slug=self.site_identifier)

    def get_search_tree_html(self, current_user: dict, show_all: bool = True):
        """
        Returns the full, nested page tree as a complete HTML string, now using the central renderer.
        """
        full_nav_data = self._build_navigation_data(
            self.tree[self.site_identifier]['__children__'], 
            current_user, 
            for_main_nav=(not show_all), 
            parent_slug=self.site_identifier
        )
        return render_html_list(full_nav_data, tag='ul', css_class='list')

    def get_sitemap_data(self, current_user: dict):
        """
        Returns the data structure for the full sitemap.
        This method IGNORES the 'visible: false' flag, showing all pages the user can access.
        The output is a list of dictionaries, intended for custom rendering.
        """
        return self._build_navigation_data(self.tree, current_user, for_main_nav=False, parent_slug="")

    def get_children_details(self, parent_identifier: str, current_user: dict, show_all_children: bool = True) -> list[str]:
        """
        Returns a list of JSON strings, each representing a direct child of the identified parent,
        using an optimized direct lookup map.
        """
        logger.debug(f"get_children_details: Started for parent_identifier='{parent_identifier}'")
        
        # Normalize the identifier: remove slashes for lookup, handle root case.
        normalized_parent_slug = parent_identifier.strip('/')
        if not normalized_parent_slug:
             normalized_parent_slug = self.site_identifier

        children_details = []
        
        # OPTIMIZED LOOKUP: Directly get the list of child slugs from the map.
        child_slugs = self.parent_to_children_map.get(normalized_parent_slug, [])
        
        for child_slug in child_slugs:
            page_data = self.page_cache.get(child_slug)
            if not page_data:
                continue

            # --- Check Access Control (CRITICAL) ---
            # We must check if the current user is allowed to see this page at all,
            # regardless of the 'show_all_children' visibility flag.
            page_access_rules = page_data.get('page', {}).get('access')
            if page_access_rules:
                has_access = self.access_checker(page_access_rules, current_user)
                if not has_access:
                    logger.debug(f"get_children_details: Skipping inaccessible child '{child_slug}' due to access rules.")
                    continue

            # --- Check Visibility (new logic for 'visible: false') ---
            # If show_all_children is False (meaning we should hide invisible pages),
            # check the 'visible' flag in the page's frontmatter meta.
            if not show_all_children:
                is_visible = page_data.get('page', {}).get('visible', True) # Defaults to True if not set
                if is_visible is False:
                    logger.debug(f"get_children_details: Skipping hidden child '{child_slug}' because show_all_children is False.")
                    continue

            # Check if this child itself has children (is a container/parent).
            # This is a quick check in the keys of our map.
            has_sub_children = child_slug in self.parent_to_children_map

            child_json_data = {
                "title": page_data.get('title', 'Untitled'),
                "url": f"/{child_slug}",
                "slug": child_slug.split('/')[-1],
                "has_children": has_sub_children
            }
            children_details.append(json.dumps(child_json_data))
            logger.debug(f"get_children_details: Found and added direct child: {child_json_data}")

        # Sort the collected children using the same logic as the main navigation.
        def sort_key_from_json_string(json_str: str) -> tuple:
            data = json.loads(json_str)
            url = data['url'].lstrip('/')
            page_info = self.page_cache.get(url)
            if page_info and 'path_parts' in page_info:
                original_part = page_info['path_parts'][-1]
                match = re.match(r'^(\d+)\.', original_part)
                if match:
                    return (0, int(match.group(1)))
                return (1, original_part)
            return (2, url) # Fallback

        sorted_children = sorted(children_details, key=sort_key_from_json_string)
        
        logger.debug(f"get_children_details: Returning {len(sorted_children)} sorted children for '{parent_identifier}'.")
        return sorted_children

    def generate_breadcrumbs(self, page_path: str, page_data: dict) -> list[dict]:
        """
        Generates a list of breadcrumb dictionaries for a given page path.
        This logic was refactored out of main.py's read_page function.
        """
        logger.debug(f"generate_breadcrumbs: Starting generation for path: '{page_path}'")
        breadcrumbs = []
        path_parts = [part for part in page_path.lower().split('/') if part]
        current_url = ""

        for i, part in enumerate(path_parts):
            # Clean the slug for the URL part
            cleaned_part = generate_clean_slug(part)
            current_url += f"/{cleaned_part}"
            
            # Determine the title for the breadcrumb, using the cleaned part as a fallback
            title = cleaned_part.replace('-', ' ').capitalize() 
            
            # Try to find a more descriptive title from the page's metadata
            if i == len(path_parts) - 1:
                # For the last part, use the page's actual title from data['page']
                title = page_data.get('page', {}).get('title', title)
            else:
                # For intermediate parts, try to find a title from the page cache
                parent_key = "/".join(path_parts[:i+1])
                page_cache_item = self.page_cache.get(parent_key)
                if page_cache_item:
                    title = page_cache_item.get('page', {}).get('title', title)
            
            # Final cleanup to ensure displayed title has no diacritics
            final_title = remove_diacritics(title)
            breadcrumbs.append({'title': final_title, 'url': current_url})
        
        logger.debug(f"generate_breadcrumbs: Generated {len(breadcrumbs)} breadcrumbs.")
        return breadcrumbs

