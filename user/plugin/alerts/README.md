# Alerts Plugin

This plugin provides a simple way to display styled alert boxes within your Markdown content. It uses a custom syntax that is processed after the main Markdown conversion, ensuring compatibility and preventing conflicts.

## How it Works

The plugin uses a Markdown Post-processor. It scans the final HTML for paragraphs that start with a specific syntax (`|`, `||`, `|||`, `||||`) and replaces the entire paragraph with a styled `<div>` element.

The plugin automatically includes the necessary CSS (`alerts.css`) and JavaScript (`alerts.js`) to style the alerts and handle optional close buttons.

## Syntax

To create an alert, start a new paragraph with one of the following syntaxes.

### Basic Alerts (No Close Button)

The number of vertical bars determines the alert's color and severity.

-   `|=` **Info:** For general information.
-   `||=` **Success:** For success messages.
-   `|||=` **Warning:** For warnings.
-   `||||=` **Danger:** For critical alerts or errors.

**Example:**

```markdown
|= This is an informational message.
|||= This is a warning message.
```

### Closable Alerts

To add a close button (`×`) to the alert, add a `+` sign before the `=`. The JavaScript file (`js/alerts.js`) will automatically handle the closing functionality.

-   `|+=` **Info** (closable)
-   `||+=` **Success** (closable)
-   `|||+=` **Warning** (closable)
-   `||||+=` **Danger** (closable)

**Example:**

```markdown
|+= This is an informational message that can be closed.
||||+= This is a danger alert that can be closed.
```
