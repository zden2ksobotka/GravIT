# user/plugin/toc/toc.py
import logging
from user.plugin.toc.toc_config import TOC_CONFIG

logger = logging.getLogger(__name__)

# The marker is an internal implementation detail of the plugin.
TOC_MARKER = '[TOC]'

def process_page_content(md_content, page_meta, extensions, extension_configs):
    """
    Processes the page content and metadata to dynamically handle the TOC.
    This function is called by the core content processor for each page.
    """
    toc_options = page_meta.get('toc', {})
    toc_enabled = toc_options.get('enabled', False)

    # Prepare toc_class and toc_style for the template, this should be done in templating.
    # We just add the config, the template will use it.
    if toc_enabled:
        toc_floating = toc_options.get('floating', False)
        page_meta['toc_class'] = 'toc-container'
        if toc_floating:
            page_meta['toc_class'] += ' floating'
        



    # Ensure [TOC] marker is present if enabled, and absent if not.
    if toc_enabled:
        if 'toc' not in extensions:
            extensions.append('toc')
        
        # Prepare a specific TOC config for this page
        page_toc_config = TOC_CONFIG.copy()
        page_toc_config['marker'] = TOC_MARKER  # Use the internal constant
        page_toc_config['toc_class'] = page_meta.get('toc_class', 'toc-container')

        baselevel = toc_options.get('baselevel')
        headinglevel = toc_options.get('headinglevel')
        if isinstance(baselevel, int) and isinstance(headinglevel, int):
            # Correctly format the depth as a "top-bottom" string per Python-Markdown documentation.
            # This correctly respects the user's desired range.
            page_toc_config['toc_depth'] = f"{baselevel}-{headinglevel}"
            logger.debug(f"TOC custom levels set: toc_depth='{page_toc_config['toc_depth']}'")
        
        extension_configs['toc'] = page_toc_config

        if TOC_MARKER not in md_content:
            md_content = f'{TOC_MARKER}\n\n' + md_content
    else:
        md_content = md_content.replace(TOC_MARKER, '')
        if 'toc' in extensions:
            extensions.remove('toc')
        if 'toc' in extension_configs:
            del extension_configs['toc']


    return md_content, page_meta, extensions, extension_configs

def register_content_processor():
    """Registers the content processor function with the core plugin system."""
    return process_page_content