# Notices Plugin

This plugin provides a simple way to display styled notice boxes (a different visual style from the "Alerts" plugin) within your Markdown content. It uses a custom syntax that is processed after the main Markdown conversion.

## How it Works

Similar to the Alerts plugin, this plugin uses a Markdown Post-processor. It scans the final HTML for paragraphs that start with a specific syntax (`!`, `!!`, `!!!`, `!!!!`) and replaces the entire paragraph with a styled `<div>` element for the notice.

The plugin automatically includes the necessary CSS (`notices.css`) and JavaScript (`notices.js`) to style the notices and handle optional close buttons.

## Syntax

To create a notice, start a new paragraph with one of the following syntaxes.

### Basic Notices (No Close Button)

The number of exclamation marks determines the notice's color and severity.

-   `!=` or `!` **Info:** For general information.
-   `!!=` or `!!` **Success:** For success messages.
-   `!!!=` or `!!!` **Warning:** For warnings.
-   `!!!!=` or `!!!!` **Danger:** For critical alerts or errors.

**Example:**

```markdown
! This is an informational notice.
!!! This is a warning notice.
```

### Closable Notices

To add a close button (`×`) to the notice, add a `+` sign before the `=`. The JavaScript file (`js/notices.js`) will automatically handle the closing functionality.

-   `!+=` **Info** (closable)
-   `!!+=` **Success** (closable)
-   `!!!+=` **Warning** (closable)
-   `!!!!+=` **Danger** (closable)

**Example:**

```markdown
!+= This is an informational notice that can be closed.
!!!!+= This is a danger notice that can be closed.
```
