import docutils.core

config = {
    'name': "reStructuredText",
    'description': "Renders reStructuredText formatted text to HTML",
    'aliases': ['rst', 'rst_filter']
    }


def run(content):
    return docutils.core.publish_parts(content, writer_name='html')['html_body']
