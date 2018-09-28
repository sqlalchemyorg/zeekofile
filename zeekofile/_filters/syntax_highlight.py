import re
import os

from pygments import util, formatters, lexers, highlight
import zeekofile_zf as zf

css_files_written = set()

code_block_re = re.compile(
    r"<pre class=\"literal-block\">\n"
    r"(?:#\!(?P<lang>\w+)\n)?"
    r"(?P<code>.*?)"
    r"</pre>", re.DOTALL
)

def highlight_code(code, language, formatter):
    try:
        lexer = lexers.get_lexer_by_name(language)
    except util.ClassNotFound:
        lexer = lexers.get_lexer_by_name("text")
    highlighted = "\n\n" + \
                  highlight(code, lexer, formatter) + \
                  "\n\n"
    return highlighted

def write_pygments_css(style, formatter, location="/css"):
    path = zf.util.path_join(zf.writer.output_dir, zf.util.fs_site_path_helper(location))
    zf.util.mkdir(path)
    css_path = os.path.join(path,"pygments_"+style+".css")
    if css_path in css_files_written:
        return #already written, no need to overwrite it.
    f = open(css_path,"w")
    f.write(formatter.get_style_defs(".pygments_"+style))
    f.close()
    css_files_written.add(css_path)

from mako.filters import html_entities_unescape

def highlight_site(code, lang="python"):
    style = zf.config.filters.syntax_highlight.style
    css_class = "pygments_"+style
    formatter = formatters.HtmlFormatter(
            linenos=False, cssclass=css_class, style=style)
    write_pygments_css(style,formatter)
    return highlight_code(code,lang,formatter)

def run(src):

    style = zf.config.filters.syntax_highlight.style
    css_class = "pygments_"+style
    formatter = formatters.HtmlFormatter(
            linenos=False, cssclass=css_class, style=style)
    write_pygments_css(style,formatter)

    def repl(m):
        lang = m.group('lang')
        code = m.group('code')

        code = html_entities_unescape(code)

        return highlight_code(code,lang,formatter)

    return code_block_re.sub(repl, src)
