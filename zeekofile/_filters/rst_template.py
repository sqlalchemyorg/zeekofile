import docutils.core

config = {
    'name': "reStructuredText",
    'description': "Renders reStructuredText formatted text to HTML",
    'aliases': ['rst', 'rst_filter']
    }


def run(content, initial_header_level=1):
    return docutils.core.publish_parts(content, writer_name='html', settings_overrides=dict(initial_header_level=initial_header_level))['html_body']

def opts(initial_header_level=1):
    def go(content):
        return run(content, initial_header_level=initial_header_level)
    return go

run.opts = opts