# Emoji Plugin

This plugin integrates with the `pymdown-extensions` library to provide rich emoji support in your Markdown content. It allows you to use standard emoji shortcodes (like `:smile:`) and automatically converts them into high-quality SVG images.

## How it Works

The plugin doesn't implement its own emoji parser. Instead, it hooks into the main application's Markdown processing pipeline and configures the built-in `pymdownx.emoji` extension.

Specifically, it sets up the following configurations:

-   **`emoji_index`**: Uses the `twemoji` index, which provides a comprehensive set of modern emojis.
-   **`emoji_generator`**: Configured to use `emoji.to_svg`, which ensures that emojis are rendered as crisp SVG images rather than standard text characters.
-   **`options`**:
    -   Sets the `image_path` to point to the SVG files located within the plugin's own directory (`/user/plugin/emoji/twemoji/svg/`).
    -   Applies default HTML attributes to the generated `<img>` tags, setting their `height` and `width` to `32px` for consistent sizing.

## Syntax

You can use standard emoji shortcodes in your Markdown files.

### Examples

```markdown
I love Python! :snake:

This is amazing! :rocket:

:smile: :laughing: :thumbsup:
```

These shortcodes will be automatically converted into SVG images during the page rendering process.
