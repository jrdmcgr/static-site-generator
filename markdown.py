"""
Markdown renderer that uses pygments to highlight code.
"""

import misaka
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


# Create a custom renderer
class CustomRenderer(misaka.HtmlRenderer):
    def blockcode(self, text, lang):
        print lang
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % text.strip()
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(text, lexer, formatter)


# And use the renderer
extensions = misaka.EXT_FENCED_CODE | misaka.EXT_NO_INTRA_EMPHASIS
render_html = misaka.Markdown(CustomRenderer(), extensions=extensions)
