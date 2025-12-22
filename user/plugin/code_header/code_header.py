"""
Code Header Plugin for the Simple CMS (Elegant & Correct Version)

This plugin wraps the code block in a custom div and then lets the
standard Markdown parser handle the code formatting itself.
"""
import re
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

class CodeHeaderPreprocessor(Preprocessor):
    """
    Finds €€€...€€€ blocks and wraps them in the necessary HTML
    and Markdown fences, letting the standard parser do the heavy lifting.
    """
    PATTERN = re.compile(r'€€€(.*?)€€€', re.DOTALL)

    def run(self, lines):
        text = "\n".join(lines)
        
        def transform_block(match):
            raw_content = match.group(1)
            
            parts = raw_content.strip().split('\n', 1)
            header = parts[0].strip()
            
            if len(parts) > 1:
                code_content = parts[1]
            else:
                code_content = ''

            # Build the wrapper div and the Markdown code fence
            transformed_block = (
                f'<div class="codeblock"><div class="codehead">{header}</div>\n'
                f'```\n{code_content}\n```\n'
                '</div>'
            )
            
            return transformed_block

        new_text = self.PATTERN.sub(transform_block, text)
        return new_text.split("\n")

class CodeHeaderExtension(Extension):
    def extendMarkdown(self, md):
        # Run with high priority to ensure it runs before the main parser
        md.preprocessors.register(CodeHeaderPreprocessor(md), 'code_header_preprocessor', 100)

def register(extensions, extension_configs):
    if not any(isinstance(ext, CodeHeaderExtension) for ext in extensions):
        extensions.append(CodeHeaderExtension())
    return extensions, extension_configs
