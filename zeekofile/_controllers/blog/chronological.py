# Write all the blog posts in reverse chronological order
from zeekofile.cache import zf

blog = zf.config.controllers.blog


def run():
    write_blog_chron(posts=blog.posts, root=blog.pagination_dir.lstrip("/"))
    write_blog_first_page()


def write_blog_chron(posts, root, name=None):
    page_num = 1
    post_num = 0

    while len(posts) > post_num:
        # Write the pages, num_per_page posts per page:
        page_posts = posts[post_num : post_num + blog.posts_per_page]
        post_num += blog.posts_per_page
        if page_num > 1:
            prev_link = "../" + str(page_num - 1)
        else:
            prev_link = None
        if len(posts) > post_num:
            next_link = "../" + str(page_num + 1)
        else:
            next_link = None
        page_dir = zf.util.path_join(blog.path, root, str(page_num))
        fn = zf.util.path_join(page_dir, "index.html")
        env = {
            "posts": page_posts,
            "next_link": next_link,
            "prev_link": prev_link,
            "name": name,
        }
        zf.writer.materialize_template("/blog/chronological.mako", fn, env)
        page_num += 1


def write_blog_first_page():
    if not blog.custom_index:
        page_posts = blog.posts[: blog.posts_per_page]
        path = zf.util.path_join(blog.path, "index.html")
        blog.logger.info("Writing blog index page: " + path)
        if len(blog.posts) > blog.posts_per_page:
            next_link = zf.util.site_path_helper(
                blog.path, blog.pagination_dir + "/2"
            )
        else:
            next_link = None
        env = {"posts": page_posts, "next_link": next_link, "prev_link": None}
        zf.writer.materialize_template("/blog/chronological.mako", path, env)
