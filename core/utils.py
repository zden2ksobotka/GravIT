# core/utils.py - Utility functions for the CMS.
import unidecode
import math


def remove_diacritics(text: str) -> str:
    """
    Removes diacritics from a string, preserving case and spaces.
    Example: "Příliš žluťoučký kůň" becomes "Prilis zlutoucky kun".
    """
    return unidecode.unidecode(text)


def generate_clean_slug(path_part: str) -> str:
    """
    Generates a URL-friendly slug from a path part, removing sorting prefixes,
    converting to lowercase, and removing diacritics.
    Example: "01.Přihlášení" becomes "prihlaseni", "Some Page" becomes "some-page".
    """
    # Remove sorting prefix if it exists
    if '.' in path_part and path_part.split('.', 1)[0].isdigit():
        path_part = path_part.split('.', 1)[1]

    # Transliterate diacritics to ASCII using the dedicated function
    ascii_part = remove_diacritics(path_part)

    # Lowercase, replace spaces with hyphens
    return ascii_part.lower().replace(' ', '-')


def render_multicolumn_list(items: list, num_columns: int, format: str = 'default') -> str:
    """
    Renders a list of items into a multi-column HTML table, filling it vertically,
    and wraps it in a container div.

    Args:
        items (list): A list of dictionaries, each with 'title' and 'url'.
        num_columns (int): The number of columns for the table.
        format (str): The list format ('none', 'num', 'list', etc.).

    Returns:
        str: The generated HTML string, including the container div.
    """
    if not items:
        return ""
        
    # Helper to clean title from accidental number prefix (e.g., if cache returns '1. Title').
    def clean_title_from_prefix(title: str) -> str:
        """Removes a numeric prefix (e.g., '1. ', '02. ') from the start of the title."""
        if title and title[0].isdigit():
            # Check for pattern 'X. ' or 'XX. ' etc.
            match = re.match(r'^(\d+\.\s)', title)
            if match:
                # Return the rest of the string after the matched prefix
                return title[len(match.group(0)):]
        return title
    
    # --- Optimization: Use standard list for one column to ensure correct indentation (num_columns == 1) ---
    if num_columns == 1:
        div_class = "one-column" 
        # Determine tag based on format
        tag = 'ol' if format == 'num' else 'ul'
        
        html = f'<{tag} class="one-column-list">'
        for item in items:
            title_html = item.get('title', 'Untitled')
            
            # Apply cleaning only if we are using the 'num' format, to prevent duplication
            if format == 'num':
                title_html = clean_title_from_prefix(title_html)
            
            url = item.get('url', '#')
            
            prefix = ""
            if format == 'num':
                 prefix = f"{items.index(item) + 1}. "
            elif format.startswith('list'):
                 # Check specific list format (e.g., 'list2' -> 🔹)
                 list_styles = {
                    'list': '🔸 ', 'list2': '🔹 ', 'list3': '🔺 ', 'list4': '◾ ', 'list5': '◽ ',
                    'list6': '● ', 'list7': '◆︎ ', 'list8': '🔷 ', 'list9': '🔶 ', 'list10': '🔴 ',
                    'list11': '🟠 ', 'list12': '🟡 ', 'list13': '🟢 ', 'list14': '🔵 ', 'list15': '🟣 ',
                    'list16': '⚪ ', 'list17': '⚫ ', 'list18': '🟦 ', 'list19': '🟩 ', 'list20': '🟥 ',
                    'list21': '🟨 ', 'list22': '🟪 ', 'list23': '⬛ '
                 }
                 prefix = list_styles.get(format, '')

            html += f'<li>{prefix}<a href="{url}">{title_html}</a></li>'
        html += f'</{tag}>'
        
        return f'<div id="container-content" class="{div_class}">{html}</div>'

    # --- Original Multi-column Table Logic (for num_columns > 1) ---
    total_items = len(items)
    items_per_column = math.ceil(total_items / num_columns)
    
    table_html = '<table class="multicolumn-list">'
    
    for row in range(items_per_column):
        table_html += '<tr>'
        for col in range(num_columns):
            item_index = row + col * items_per_column
            if item_index < total_items:
                item = items[item_index]
                title_html = item.get('title', 'Untitled')
                
                # Apply cleaning only if we are using the 'num' format, to prevent duplication
                if format == 'num':
                    title_html = clean_title_from_prefix(title_html)
                    
                url = item.get('url', '#')
                
                prefix = ""
                if format == 'num':
                    prefix = f"{item_index + 1}. "
                elif format == 'list':
                    prefix = "🔸 "
                elif format == 'list2':
                    prefix = "🔹 "
                elif format == 'list3':
                    prefix = "🔺 "
                elif format == 'list4':
                    prefix = "◾ "
                elif format == 'list5':
                    prefix = "◽ "
                elif format == 'list6':
                    prefix = "● "
                elif format == 'list7':
                    prefix = "◆︎ "
                elif format == 'list8':
                    prefix = "🔷 "
                elif format == 'list9':
                    prefix = "🔶 "
                elif format == 'list10':
                    prefix = "🔴 "
                elif format == 'list11':
                    prefix = "🟠 "
                elif format == 'list12':
                    prefix = "🟡 "
                elif format == 'list13':
                    prefix = "🟢 "
                elif format == 'list14':
                    prefix = "🔵 "
                elif format == 'list15':
                    prefix = "🟣 "
                elif format == 'list16':
                    prefix = "⚪ "
                elif format == 'list17':
                    prefix = "⚫ "
                elif format == 'list18':
                    prefix = "🟦 "
                elif format == 'list19':
                    prefix = "🟩 "
                elif format == 'list20':
                    prefix = "🟥 "
                elif format == 'list21':
                    prefix = "🟨 "
                elif format == 'list22':
                    prefix = "🟪 "
                elif format == 'list23':
                    prefix = "⬛ "
                
                table_html += f'<td>{prefix}<a href="{url}">{title_html}</a></td>'
            else:
                table_html += '<td></td>'  # Empty cell if no more items
        table_html += '</tr>'
    table_html += '</table>'
    div_class = "multi-column"
    return f'<div id="container-content" class="{div_class}">{table_html}</div>'

    def parse_container_config(page_meta: dict, current_user_is_logged_in: bool) -> tuple:
        """
        Parses container configuration from page metadata, handling nested 'show_all' logic.
        Returns:
            tuple: (is_container: bool, num_columns: int, list_format: str, show_all_children: bool)
        """
        container_config = page_meta.get('container')

        is_container = False
        num_columns = 1
        list_format = 'list2'
        show_all_children = True

        if isinstance(container_config, dict):
            is_container = container_config.get('enabled', False)
            num_columns = container_config.get('columns', 1)
            list_format = container_config.get('format', 'list2')

            show_all_config = container_config.get('show_all', True)

            if isinstance(show_all_config, dict):
                # Complex configuration: show_all: {when_logout: ..., when_login: ...}
                key_to_use = 'when_login' if current_user_is_logged_in else 'when_logout'
                show_all_children = show_all_config.get(key_to_use, True)
            elif isinstance(show_all_config, bool):
                # Simple configuration: show_all: true/false (stará logika)
                show_all_children = show_all_config

        elif container_config is True:
            is_container = True
            # For backward compatibility, container: True defaults to a numbered list, show_all_children=True.
            list_format = 'num'

        return is_container, num_columns, list_format, show_all_children

    def render_html_list(items: list, tag: str = 'ul', is_root: bool = True, css_class: str = 'list') -> str:
        """
        Recursively renders a nested HTML list (ul or ol) from a list of item dictionaries.
        Args:
            items (list): A list of dictionaries, where each dict can contain 'title', 'url',
                          'children', 'has_children', and 'is_container'.
            tag (str): The HTML tag to use for the list ('ul' or 'ol').
            is_root (bool): Whether this is the top-level call to add the main CSS class.
            css_class (str): The CSS class to apply to the root list element.
        Returns:
            str: The generated HTML string.
        """

        if not items:
            return ""

        class_attr = f' class="{css_class}"' if is_root and css_class else ''
        html = f"<{tag}{class_attr}>"

        for item in items:
            title_html = item.get('title', 'Untitled')
            url = item.get('url', '#')

            # In a generic list, a container with children should be visually distinct
            if item.get('has_children', False):
                title_html = f"<strong>{title_html}</strong>"

            # In the main menu, containers are non-clickable spans.
            # This condition makes the function versatile for both menus and index lists.
            if item.get('url') == '#':
                 list_item_content = f'<span class="nav-item container-item">{title_html}</span>'
            else:
                 list_item_content = f'<a href="{url}">{title_html}</a>'
            html += f"<li>{list_item_content}"

            # Recursive call for children
            if item.get('children'):
                html += render_html_list(item['children'], tag=tag, is_root=False)
            html += "</li>"
        html += f"</{tag}>"
        return html

def parse_container_config(page_meta: dict, current_user_is_logged_in: bool) -> tuple:
    """
    Parses container configuration from page metadata, handling nested 'show_all' logic.
    
    Returns:
        tuple: (is_container: bool, num_columns: int, list_format: str, show_all_children: bool)
    """
    container_config = page_meta.get('container')

    is_container = False
    num_columns = 1
    list_format = 'list2'
    show_all_children = True
    
    if isinstance(container_config, dict):
        is_container = container_config.get('enabled', False)
        num_columns = container_config.get('columns', 1)
        list_format = container_config.get('format', 'list2')
        
        show_all_config = container_config.get('show_all', True)
        
        if isinstance(show_all_config, dict):
            # Complex configuration: show_all: {when_logout: ..., when_login: ...}
            key_to_use = 'when_login' if current_user_is_logged_in else 'when_logout'
            show_all_children = show_all_config.get(key_to_use, True)
        elif isinstance(show_all_config, bool):
            # Simple configuration: show_all: true/false (stará logika)
            show_all_children = show_all_config
            
    elif container_config is True:
        is_container = True
        # For backward compatibility, container: True defaults to a numbered list, show_all_children=True.
        list_format = 'num'
        
    return is_container, num_columns, list_format, show_all_children


def render_html_list(items: list, tag: str = 'ul', is_root: bool = True, css_class: str = 'list') -> str:
    """
    Recursively renders a nested HTML list (ul or ol) from a list of item dictionaries.

    Args:
        items (list): A list of dictionaries, where each dict can contain 'title', 'url',
                      'children', 'has_children', and 'is_container'.
        tag (str): The HTML tag to use for the list ('ul' or 'ol').
        is_root (bool): Whether this is the top-level call to add the main CSS class.
        css_class (str): The CSS class to apply to the root list element.

    Returns:
        str: The generated HTML string.
    """
    if not items:
        return ""

    class_attr = f' class="{css_class}"' if is_root and css_class else ''
    html = f"<{tag}{class_attr}>"

    for item in items:
        title_html = item.get('title', 'Untitled')
        url = item.get('url', '#')
        
        # In a generic list, a container with children should be visually distinct
        if item.get('has_children', False):
            title_html = f"<strong>{title_html}</strong>"

        # In the main menu, containers are non-clickable spans.
        # This condition makes the function versatile for both menus and index lists.
        if item.get('url') == '#':
             list_item_content = f'<span class="nav-item container-item">{title_html}</span>'
        else:
             list_item_content = f'<a href="{url}">{title_html}</a>'

        html += f"<li>{list_item_content}"
        
        # Recursive call for children
        if item.get('children'):
            html += render_html_list(item['children'], tag=tag, is_root=False)
        
        html += "</li>"

    html += f"</{tag}>"
    return html


def wrap_in_container_div(html_content: str) -> str:
    """Wraps the given HTML content in a container div for styling."""
    return f'<div class="container-div">{html_content}</div>'
