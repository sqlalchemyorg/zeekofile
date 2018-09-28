from zeekofile.cache import zf

blog = zf.config.controllers.blog


def run():
    write_feed(blog.posts, zf.util.path_join(blog.path, "feed"), "/blog/rss.mako")
    write_feed(blog.posts, zf.util.path_join(blog.path, "feed", "atom"),
                          "/blog/atom.mako")

def write_feed(posts, root, template):
    root = root.lstrip("/")
    path = zf.util.path_join(root, "index.xml")
    blog.logger.info("Writing RSS/Atom feed: " + path)
    env = {"posts": posts, "root": root}
    zf.writer.materialize_template(template, path, env)
