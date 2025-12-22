# Search Plugin

This plugin provides a comprehensive, interactive search functionality for the website. It combines a server-side search endpoint with client-side JavaScript to deliver a fast, "live search" experience without full page reloads.

## How it Works

The plugin is composed of two main parts: a backend API endpoint and frontend logic.

### Backend (FastAPI Endpoint)

-   **Route Registration:** The plugin registers a `/search` endpoint in the main application. This endpoint accepts a query parameter `q` (e.g., `/search?q=linux`).
-   **Data Source:** The search is performed against the in-memory `PAGE_CACHE`, which contains the pre-loaded content of all pages. This makes the search operation extremely fast.
-   **Search Logic:**
    1.  It takes the user's query `q`.
    2.  It iterates through the content of all pages in the cache.
    3.  It finds all occurrences of the query string (case-insensitively).
    4.  Pages are ranked by the number of matches.
    5.  For each matching page, it generates short snippets of the surrounding text and highlights the search term with `<mark>` tags.
-   **HTML Fragment Response:** The endpoint does not return a full HTML page. Instead, it renders a partial Twig template (`partials/search-results.html.twig`) that contains only the list of search results. This small HTML fragment is then sent back to the browser.

### Sitemap Display

-   If the search query `q` is empty or too short, the endpoint does not perform a search. Instead, it displays a full, hierarchical sitemap of the website.
-   It uses the global `NavigationBuilder` instance to generate the sitemap HTML, ensuring consistency with the main navigation and respect for user access permissions.

### Frontend (JavaScript)

-   The theme's main JavaScript file (`main.js`) contains the logic to handle the search interface.
-   When a user types into the search box, the JavaScript waits for a short pause (300ms debounce) and then sends an asynchronous `fetch` request to the `/search` endpoint with the current query.
-   When it receives the HTML fragment from the server, it injects it directly into the `search-results` container on the page, instantly updating the view without a page refresh.

This combination of a fast backend and dynamic frontend provides a seamless and responsive user experience.
