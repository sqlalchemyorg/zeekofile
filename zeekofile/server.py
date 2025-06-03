from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
import logging
import os
import re
import sys
import threading
from urllib.parse import urlparse

from . import config
from . import util
from .cache import zf

zf.server = sys.modules["zeekofile.server"]

logger = logging.getLogger("zeekofile.server")


class Server(threading.Thread):

    def __init__(self, port, address="127.0.0.1"):
        self.port = int(port)
        self.address = address
        if self.address == "0.0.0.0":
            address = ""
        threading.Thread.__init__(self)
        self.is_shutdown = False
        server_address = (address, self.port)
        HandlerClass = ZFRequestHandler
        ServerClass = HTTPServer
        HandlerClass.protocol_version = "HTTP/1.0"
        self.httpd = ServerClass(server_address, HandlerClass)
        self.sa = self.httpd.socket.getsockname()

    def run(self):
        print(
            "Zeekofile server started on {0}:{1} ...".format(
                self.sa[0], self.sa[1]
            )
        )
        self.httpd.serve_forever()

    def shutdown(self):
        print("\nshutting down webserver...")
        self.httpd.shutdown()
        self.httpd.socket.close()
        self.is_shutdown = True


class ZFRequestHandler(SimpleHTTPRequestHandler):

    error_template = """
<head>
<title>Error response</title>
</head>
<body>
<h1>404 Error</h1>
Your zeekofile site is configured for a subdirectory, maybe you were looking
for the root page? : <a href="{0}">{1}</a>
</body>"""

    def __init__(self, *args, **kwargs):
        path = urlparse(config.site.url).path
        self.error_template = self.error_template.format(path, path)
        SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)

    def translate_path(self, path):
        site_path = urlparse(config.site.url).path
        if len(site_path.strip("/")) > 0 and not path.startswith(site_path):
            self.error_message_format = self.error_template
            return ""  # Results in a 404

        p = SimpleHTTPRequestHandler.translate_path(self, path)
        if len(site_path.strip("/")) > 0:
            build_path = os.path.join(
                os.getcwd(), util.path_join(site_path.strip("/"))
            )
        else:
            build_path = os.getcwd()
        build_path = re.sub(build_path, os.path.join(os.getcwd(), "_site"), p)
        return build_path

    def log_message(self, format, *args):
        pass
