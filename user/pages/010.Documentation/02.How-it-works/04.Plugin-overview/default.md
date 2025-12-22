---
title: "Overview of Key Plugins"
slug: "plugins-overview"
---
! This CMS utilizes a modular plugin system to extend its core functionality. Here is an overview of the most important ones you might encounter.

### Plugins for Content and Appearance

*   **Alerts & Notices:** Allow inserting colored informational boxes using syntax like `!` or `|`.
*   **Emoji:** Converts shortcodes (e.g., `:smile:`) into graphical emojis.
*   **TOC (Table of Contents):** Automatically generates the table of contents from page headings.
*   **Author:** Displays the author's name and publication date below the article (if defined in YAML).

### Functional and Diagnostic Plugins

Some plugins add special pages (routes) to the system, which are usually intended for diagnostics or specific functions.

*   **Search:** Handles all the logic for site-wide searching.
*   **Page Tree:** Generates a complete sitemap (tree structure).
    *   **URL:** [`/tree`](/tree)
*   **Memory Stats:** Displays statistics on memory usage by individual application processes. Useful for performance debugging.
    *   **URL:** [`/memory_stats`](/memory_stats)
*   **Test Dump Page Cache:** Outputs the complete content of the `PAGE_CACHE` to a text file. Intended exclusively for developers and debugging.
    *   **URL:** [`/dumpcache`](/dumpcache)
*   **Optimizer:** Generates and manages a Service Worker in the background, which caches static files (CSS, JS) in the browser for significantly faster repeated page loads.
*   **Page Statistics:** A simple system for tracking the number of views for individual pages.


---
**[Back to "How It Works" overview](/doku/how-it-works)** | **[Back to the absolute start of the demo](/doku)**
