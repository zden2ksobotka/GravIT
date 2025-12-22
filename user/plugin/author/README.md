# Author Plugin

This plugin provides a simple and robust way to display the author's name and the page's publication date.

## How it Works

The plugin is designed to be fully self-contained and intelligent. It exposes a global template function `get_author_signature(page.slug)` that can be called from any template.

1.  **Data Source**: The function uses the page `slug` to look up the complete page data in the central `PAGE_CACHE`.
2.  **Metadata Extraction**: It specifically looks for two flattened metadata keys:
    *   `_page.taxonomy.author`: The author's name.
    *   `_page.date`: The publication date.
3.  **Intelligent Formatting**: The plugin handles various scenarios gracefully:
    *   If only the author is present, it displays just the author's name.
    *   If only the date is present, it displays just the formatted date.
    *   If both are present, it displays them joined by a comma (e.g., `zden2k, 2019-02-12`).
    *   If neither is present, it displays nothing.
4.  **Robust Date Handling**: The date processing logic can handle `datetime` objects, timestamps, or simple strings, always formatting the output to `YYYY-MM-DD`.

## Usage in Templates

To display the author signature, simply call the function in your Twig template, passing the page's slug:

```twig
{% if 'author' in active_plugin_names and page.slug is defined %}
    {{ get_author_signature(page.slug) | safe }}
{% endif %}
```
