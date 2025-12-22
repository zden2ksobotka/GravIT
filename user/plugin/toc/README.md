# Table of Contents (TOC) Plugin

This plugin dynamically generates a "Table of Contents" for any page based on its headings (h1, h2, h3, etc.). The behavior of the TOC is controlled directly from the YAML frontmatter of each individual page, allowing for maximum flexibility.

## How it Works

The plugin has evolved significantly. Instead of relying on a manual `[TOC]` marker, the generation is now handled automatically by the core logic in `core/content.py` based on settings in the page's frontmatter.

1.  **YAML Configuration:** The system checks the `toc` section in a page's YAML frontmatter.
2.  **Automatic Generation:** If `toc.enabled` is `true`, the core content processor automatically inserts a TOC marker at the beginning of the Markdown content before processing. This ensures the TOC is always generated. If `enabled` is `false` or missing, any accidental `[TOC]` markers are removed to prevent them from appearing as plain text.
3.  **Dynamic Styling:** The core logic also checks for `toc.floating`. Based on this value, it dynamically adds CSS classes (`toc-container`, `floating`) to the generated TOC `<div>`. This allows the final CSS to control the layout (either as a standard block or a floating box) without needing separate logic in the template.

The plugin's primary roles are now:
*   To provide the default configuration for the Markdown `toc` extension (`toc_config.py`).
*   To supply the necessary CSS (`_toc.scss`) and the compiler (`compile.sh`) for styling the final output.

## Usage

To display a Table of Contents, simply add the `toc` configuration to your page's YAML frontmatter. **The `[TOC]` marker in the content is no longer needed.**

### Basic Usage (Standard Block)

To show the TOC as a standard block at the top of your content, use:

```yaml
---
title: "My Awesome Page"
slug: "awesome-page"
toc:
  enabled: true
---

# First Heading
...
```

### Floating TOC (Obtékaný textem)

To display the TOC as a floating box on the right side of the content (on desktop screens), use:

```yaml
---
title: "My Awesome Page"
slug: "awesome-page"
toc:
  enabled: true
  floating: true
---

# First Heading
...
```

If `floating` is set to `false` or is omitted, the TOC will render as a standard block.

## Styling and Customization

The plugin uses SCSS for dynamic and flexible styling.

*   **Source File:** `user/plugin/toc/css/_toc.scss`
*   **Compiler:** `user/plugin/toc/compile.sh`

The CSS is designed to be easily customizable:
*   **Fonts:** The plugin now downloads and locally hosts the "Roboto Condensed" font for a clean, modern look. The font files are located in `user/plugin/toc/fonts/`.
*   **Layout:** The `_toc.scss` file contains two main selectors:
    *   `.toc-container`: Defines the basic styles (background, border, padding).
    *   `.toc-container.floating`: Contains the styles for the floating version (`float: right`, `max-width`, etc.), which are applied only on screens wider than 1012px.
*   **Recompiling:** After making any changes to `_toc.scss`, you must run the compiler from the project root to apply them:
    ```bash
    ./user/plugin/toc/compile.sh
    ```
This will regenerate the final `user/plugin/toc/css/toc.css` file that is served to the browser.