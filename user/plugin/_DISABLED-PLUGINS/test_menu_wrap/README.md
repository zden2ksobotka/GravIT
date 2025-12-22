# Page Tree Plugin

This plugin provides a dedicated API endpoint to retrieve a complete, hierarchical sitemap of the website as a raw HTML fragment.

## How it Works

The plugin registers a new route, `/tree`, within the FastAPI application. When a request is made to this endpoint, it performs the following actions:

1.  **Accesses the Navigation Builder:** It uses a function provided by the core application (`get_nav_builder`) to get access to the global `NavigationBuilder` instance. This instance already contains the complete, cached page hierarchy.
2.  **Retrieves Current User:** It determines the current user (logged in or anonymous) to ensure that the generated sitemap respects all access permissions.
3.  **Generates HTML:** It calls the `nav_builder.get_search_tree_html()` method. This method traverses the page tree and generates a nested, unordered HTML list (`<ul>...</ul>`) representing the sitemap. It automatically filters out any pages the current user is not allowed to see.
4.  **Returns HTML Fragment:** The plugin combines the generated HTML list with a hardcoded `<h3>` title and returns it directly as an `HTMLResponse`. It does not render a full page template, making it a lightweight and fast endpoint suitable for being called via JavaScript (AJAX) or for simple embedding.

## Usage

The primary purpose of this plugin is to provide a sitemap that can be displayed in various parts of the theme, such as the search page, without duplicating the sitemap generation logic.
