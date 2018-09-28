import markdown
import logging

#Markdown logging is noisy, pot it down:
logging.getLogger("MARKDOWN").setLevel(logging.ERROR)

config = {
    'name': "Markdown",
    'description': "Renders markdown formatted text to HTML",
    'aliases': ['markdown']
    }

def run(content):
    return markdown.markdown(content)
