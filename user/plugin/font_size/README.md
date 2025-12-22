# Font Size Plugin

This plugin provides a simple and safe way to override the base font size of the entire website, allowing for easy customization and improved accessibility. It supports different font sizes for desktop and mobile viewports.

## How it Works

The plugin leverages SCSS for dynamic CSS generation, ensuring a clean and maintainable approach.

1.  **Configuration:** The plugin's behavior is controlled by a simple configuration file: `font_size_config.py`. Here, you can enable or disable the font size override for desktop and mobile independently, and set the desired font size percentages.

2.  **SCSS Compilation:** On application startup, the plugin's `register()` function is called. This function reads the values from the configuration file.

3.  **Dynamic CSS Generation:** It then takes a template SCSS file (`_font_size.scss`) and injects the configuration values as SCSS variables. Using the `libsass` library, it compiles this SCSS code into a final CSS file: `css/font_size.css`.

4.  **Conditional Generation:** The logic is designed to be robust:
    -   If both desktop and mobile are enabled, the CSS file will contain rules for both.
    -   If only one is enabled, the final CSS will only contain the relevant rule.
    -   If both are disabled, the `font_size.css` file is automatically deleted, ensuring no unnecessary styles are loaded.

5.  **Automatic Injection:** The core CMS logic automatically detects the presence of the generated `font_size.css` file and includes it in the website's HTML head, but only if the file actually exists.

This method ensures that the theme's original CSS files are never modified. The plugin's styles are applied on top of the theme's styles, and the `!important` rule ensures they take precedence.

## Configuration

All settings are located in `user/plugin/font_size/font_size_config.py`.

-   `ENABLED_DESKTOP`: Set to `True` or `False` to enable the desktop font size override.
-   `ENABLED_MOBILE`: Set to `True` or `False` to enable the mobile font size override.
-   `DESKTOP_FONT_SIZE_PERCENT`: A number representing the base font size percentage for desktops (e.g., `100`).
-   `MOBILE_FONT_SIZE_PERCENT`: A number representing the base font size percentage for mobiles (e.g., `95`).
-   `MOBILE_BREAKPOINT_PX`: The screen width in pixels below which the mobile size is applied (e.g., `800`).
