
from pymdownx import emoji

def register(extensions, extension_configs):
    # Změna 'emoji_index' na 'emoji.twemoji'
    # Tento index mapuje technické kódy (např. 1f600) na správné znaky,
    # což je přesně to, co potřebujeme.
    extension_configs['pymdownx.emoji'] = {
        'emoji_index': emoji.twemoji,
        'emoji_generator': emoji.to_svg,
        'options': {
            'image_path': '/user/plugin/emoji/twemoji/svg/',
            'attributes': {
                'align': 'absmiddle',
            }
        }
    }
    extensions.append('pymdownx.emoji')
    return extensions, extension_configs

