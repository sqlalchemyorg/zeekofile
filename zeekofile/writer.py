#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
writer.py writes out the static blog to ./_site based on templates found in the
current working directory.
"""

import logging
import os
import stat
import shutil
import tempfile
from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions as mako_exceptions

from . import config, util, cache, filter, controller

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"


logger = logging.getLogger("zeekofile.writer")


def _file_mtime(f):
    if not os.path.exists(f):
        return None
    else:
        st = os.stat(f)
        return st[stat.ST_MTIME]


def _check_output(state, output_dir):
    starting = not(state)
    for src, dest in _walk_files(output_dir, True):
        src_mtime = _file_mtime(src)
        if starting:
            state[src] = src_mtime
        elif src_mtime > state.get(src, 0):
            logger.info("File %s changed since start", src)
            state[src] = src_mtime
            print("File changes detected, rebuilding...")
            _rebuild()
            break


def _rebuild(output_dir):
    writer = Writer()
    writer.write_site(output_dir)


def _walk_files(output_dir, include_src_templates):

    for root, dirs, files in os.walk("."):
        if root.startswith("./"):
            root = root[2:]

        for d in list(dirs):
            #Exclude some dirs
            d_path = util.path_join(root,d)
            if util.should_ignore_path(d_path) and (
                not include_src_templates or
                not d.startswith('_') or
                d.startswith("_site")
            ):
                dirs.remove(d)

        for t_fn in files:
            t_fn_path = util.path_join(root, t_fn)
            if util.should_ignore_path(t_fn_path):
                #Ignore this file.
                logger.debug("Ignoring file: " + t_fn_path)
                continue
            elif t_fn.endswith(".mako"):
                t_name = t_fn[:-5]
                path = util.path_join(output_dir, root, t_name)
                yield t_fn_path, path
            else:
                f_path = util.path_join(root, t_fn)
                out_path = util.path_join(output_dir, f_path)
                yield f_path, out_path


class Writer(object):

    def __init__(self):
        self.config = config
        #Base templates are templates (usually in ./_templates) that are only
        #referenced by other templates.
        self.base_template_dir = util.path_join(".", "_templates")
        self.output_dir = tempfile.mkdtemp()
        self.template_lookup = TemplateLookup(
                directories=[".", self.base_template_dir],
                input_encoding='utf-8', output_encoding='utf-8',
                encoding_errors='replace')

    def _load_bf_cache(self):
        self.bf = cache.bf
        self.bf.writer = self
        self.bf.logger = logger

    def write_site(self, output_dir):
        self._load_bf_cache()
        self._init_filters_controllers()
        self._run_controllers()
        self._write_files()
        self._copy_to_site(output_dir)

    def copyfile(self, src, dest):
        logger.debug("Copying file: " + src)
        shutil.copyfile(src, dest)

    def _copy_to_site(self, output_dir):
        files_ = []
        self._copytree(self.output_dir, output_dir, files_)
        shutil.rmtree(self.output_dir)
        files_ = set(files_)
        for root, dirs, files in os.walk(output_dir):
            for file_ in files:
                path = os.path.join(root, file_)
                relative_name = path[len(output_dir):]
                if relative_name not in files_:
                    logger.info("Deleting: %s", path)
                    os.remove(path)

    def _copytree(self, src, dst, files_):
        names = os.listdir(src)
        util.mkdir(dst)
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            if os.path.isdir(srcname):
                self._copytree(srcname, dstname, files_)
            else:
                shutil.copy2(srcname, dstname)
            relative_name = os.path.normpath(srcname[len(self.output_dir):])
            files_.append(relative_name)

    def _write_files(self):
        """Write all files for the blog to _site

        Convert all templates to straight HTML
        Copy other non-template files directly"""

        for src, dest in _walk_files(self.output_dir, False):
            if not os.path.exists(os.path.dirname(dest)):
                util.mkdir(os.path.dirname(dest))

            if src.endswith(".mako"):
                #Process this template file
                with open(src, encoding='utf-8') as t_file:
                    template = Template(t_file.read(),
                                        lookup=self.template_lookup,
                                        output_encoding=None)
                    #Remember the original path for later when setting context
                    template.bf_meta = {"path": src}

                with self._output_file(dest) as html_file:
                    html = self.template_render(template)
                    #Write to disk
                    html_file.write(html)
            else:
                self.copyfile(src, dest)

    def _init_filters_controllers(self):
        #Run filter/controller defined init methods
        filter.init_filters()
        controller.init_controllers()

    def _run_controllers(self):
        """Run all the controllers in the _controllers directory"""
        controller.run_all()

    def _output_file(self, name):
        return open(name, 'w', encoding='utf-8')

    def template_render(self, template, attrs={}):
        """Render a template"""
        # Create a context object that is fresh for each template render
        self.bf.template_context = cache.Cache(**attrs)
        # Provide the name of the template we are rendering:
        self.bf.template_context.template_name = template.uri
        try:
            # Static pages will have a template.uri like memory:0x1d80a90
            # We conveniently remembered the original path to use instead.
            self.bf.template_context.template_name = template.bf_meta['path']
        except AttributeError:
            pass
        attrs['bf'] = self.bf
        # Provide the template with other user defined namespaces:
        for name, obj in self.bf.config.site.template_vars.items():
            attrs[name] = obj
        try:
            return template.render_unicode(**attrs)
        except:
            logger.error("Error rendering template")
            print(mako_exceptions.text_error_template().render())
        del self.bf.template_context

    def materialize_template(self, template_name, location, attrs={}):
        """Render a named template with attrs to a location in the _site dir"""
        logger.info("Materialize template: %s", location)
        template = self.template_lookup.get_template(template_name)
        template.output_encoding = "utf-8"
        rendered = self.template_render(template, attrs)
        path = util.path_join(self.output_dir, location)
        #Create the path if it doesn't exist:
        util.mkdir(os.path.split(path)[0])
        with self._output_file(path) as f:
            f.write(rendered)
