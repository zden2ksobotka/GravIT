"""
Notices Plugin for the Simple CMS

This plugin uses a custom Markdown Post-processor to find paragraphs
starting with notice syntax (e.g., `|= My message`) and converts them
directly into the final HTML <div> for the notice.
"""
import re
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

class NoticesPostprocessor(Postprocessor):
    """
    This postprocessor finds paragraphs like `<p>! text</p>`, `<p>!= text</p>` or `<p>!+= text</p>`
    and replaces them with the appropriate HTML structure.
    """
    # This pattern handles all cases: `! text`, `!= text`, and `!+= text`
    PATTERN = re.compile(r'<p>(\!{1,4})(?:(\+)=|=?)\s?(.*?)</p>', re.DOTALL)

    def run(self, text):
        """
        Find and replace all notice paragraphs.
        """
        return self.PATTERN.sub(self.replace_match, text)

    def replace_match(self, match):
        """
        Callback function for re.sub. Takes a match object and returns
        the replacement HTML string.
        """
        # The regex ensures that group structure is ('!', <'+' or None>, 'content')
        notice_type_str, closable_marker, content = match.groups()
        
        notice_map = {
            '!': 'info',
            '!!': 'success',
            '!!!': 'warning',
            '!!!!': 'danger'
        }
        
        css_class = notice_map.get(notice_type_str, 'info')
        
        # Add the 'closable' class only if the '+' marker was present
        if closable_marker:
            return f'<div class="notice {css_class} closable">{content.strip()}</div>'
        else:
            return f'<div class="notice {css_class}">{content.strip()}</div>'

class NoticesExtension(Extension):
    """
    This extension registers the NoticesPostprocessor.
    """
    def extendMarkdown(self, md):
        md.postprocessors.register(NoticesPostprocessor(md), 'notices_postprocessor', 0)

def register(extensions, extension_configs):
    """
    This is the main registration function called by the CMS.
    It simply registers our custom, self-contained NoticesExtension.
    """
    if not any(isinstance(ext, NoticesExtension) for ext in extensions):
        extensions.append(NoticesExtension())

    return extensions, extension_configs
