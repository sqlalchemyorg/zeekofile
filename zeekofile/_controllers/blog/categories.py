import operator
import shutil

from zeekofile.cache import zf
from . import feed

blog = zf.config.controllers.blog


def run():
    write_categories()


def sort_into_categories():
    categories = set()
    for post in blog.posts:
        categories.update(post.categories)
    for category in categories:
        category_posts = [
            post for post in blog.posts if category in post.categories
        ]
        blog.categorized_posts[category] = category_posts
    for category, posts in sorted(
        blog.categorized_posts.items(), key=operator.itemgetter(0)
    ):
        blog.all_categories.append((category, len(posts)))


def write_categories():
    """Write all the blog posts in categories"""
    root = zf.util.path_join(blog.path, blog.category_dir)
    # Find all the categories:
    categories = set()
    for post in blog.posts:
        categories.update(post.categories)
    for category, category_posts in blog.categorized_posts.items():
        # Write category RSS feed
        rss_path = zf.util.fs_site_path_helper(
            blog.path, blog.category_dir, category.url_name, "feed"
        )
        feed.write_feed(category_posts, rss_path, "/blog/rss.mako")
        atom_path = zf.util.fs_site_path_helper(
            blog.path, blog.category_dir, category.url_name, "feed", "atom"
        )
        feed.write_feed(category_posts, atom_path, "/blog/atom.mako")
        page_num = 1
        while True:
            path = zf.util.path_join(
                root, category.url_name, str(page_num), "index.html"
            )
            page_posts = category_posts[: blog.posts_per_page]
            category_posts = category_posts[blog.posts_per_page :]
            # Forward and back links
            if page_num > 1:
                prev_link = zf.util.site_path_helper(
                    blog.path,
                    blog.category_dir,
                    category.url_name,
                    str(page_num - 1),
                )
            else:
                prev_link = None
            if len(category_posts) > 0:
                next_link = zf.util.site_path_helper(
                    blog.path,
                    blog.category_dir,
                    category.url_name,
                    str(page_num + 1),
                )
            else:
                next_link = None

            env = {
                "category": category,
                "posts": page_posts,
                "prev_link": prev_link,
                "next_link": next_link,
            }
            zf.writer.materialize_template(
                "/blog/chronological.mako", path, env
            )

            # Copy category/1 to category/index.html
            if page_num == 1:
                shutil.copyfile(
                    zf.util.path_join(zf.writer.output_dir, path),
                    zf.util.path_join(
                        zf.writer.output_dir,
                        root,
                        category.url_name,
                        "index.html",
                    ),
                )
            # Prepare next iteration
            page_num += 1
            if len(category_posts) == 0:
                break
