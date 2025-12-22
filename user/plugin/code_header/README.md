# Code Header Plugin

This plugin allows you to create styled code blocks that include a distinct header section, perfect for displaying file names, titles, or programming languages.

## How it Works

The plugin utilizes a Markdown Post-processor that runs after the standard Markdown-to-HTML conversion. It specifically looks for paragraphs that are wrapped in a custom `€€€...€€€` syntax.

When a match is found, the entire paragraph is replaced with a structured HTML `<div>` containing a header and a `<pre><code>` block. The content inside the code block is automatically HTML-escaped to prevent XSS vulnerabilities and ensure correct rendering.

The necessary CSS for styling the code block and its header is automatically included from the plugin's `css/code_header.css` file.

## Syntax

To create a code block with a header, wrap your content in `€€€` on a new paragraph.

-   The **first line** after the opening `€€€` is treated as the **header text**.
-   All subsequent lines are treated as the **code content**.

### Example

```markdown
€€€path/to/your/file.py
print("Hello, World!")

def my_function():
    return True
€€€
```

This will be converted into the following HTML structure:

```html
<div class="codeblock">
    <div class="codehead">path/to/your/file.py</div>
    <pre><code>print("Hello, World!")

def my_function():
    return True</code></pre>
</div>
```
