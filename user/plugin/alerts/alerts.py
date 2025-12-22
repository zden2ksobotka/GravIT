"""
Alerts Plugin for the Simple CMS

This plugin uses a custom Markdown Post-processor to find paragraphs
starting with alert syntax (e.g., `! My message`) and converts them
directly into the final HTML <div> for the alert.

This method is robust and avoids conflicts with other Markdown syntax.

Based on:
https://www.w3schools.com/howto/howto_js_alert.asp
"""
import re
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

class AlertsPostprocessor(Postprocessor):
    """
    This postprocessor finds paragraphs like `<p>!= text</p>` or `<p>!+= text</p>`
    and replaces them with the appropriate HTML structure.
    """
    PATTERN = re.compile(r'<p>(\|{1,4})(\+)?=(.*?)</p>', re.DOTALL)

    def run(self, text):
        """
        Find and replace all alert paragraphs.
        """
        return self.PATTERN.sub(self.replace_match, text)

    def replace_match(self, match):
        """
        Callback function for re.sub. Takes a match object and returns
        the replacement HTML string.
        """
        alert_type_str, closable_marker, content = match.groups()
        
        # Map the captured exclamation marks to CSS classes
        alert_map = {
            '|': 'info',
            '||': 'success',
            '|||': 'warning',
            '||||': 'danger'
        }
        
        # Get the CSS class, default to 'info' if something unexpected happens
        css_class = alert_map.get(alert_type_str, 'info')
        
        # Add the 'closable' class only if the '+' marker was present
        if closable_marker:
            return f'<div class="alert {css_class} closable">{content}</div>'
        else:
            return f'<div class="alert {css_class}">{content}</div>'

class AlertsExtension(Extension):
    """
    This extension registers the AlertsPostprocessor.
    """
    def extendMarkdown(self, md):
        # Register the postprocessor to run after all other processing is done.
        # A low priority number means it runs late.
        md.postprocessors.register(AlertsPostprocessor(md), 'alerts_postprocessor', 0)

def register(extensions, extension_configs):
    """
    This is the main registration function called by the CMS.
    It simply registers our custom, self-contained AlertsExtension.
    """
    # Add our custom extension. It handles everything internally.
    if not any(isinstance(ext, AlertsExtension) for ext in extensions):
        extensions.append(AlertsExtension())

    return extensions, extension_configs
