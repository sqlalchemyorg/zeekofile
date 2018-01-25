=========
zeekofile
=========

This is zzzeek's fork of the amazing and unmaintained Blogofile, the
static website compiler written by Ryan McGuire for Mako and Jinja2 templates.

The fork exists because my websites sqlalchemy.org and zzzeek.org were built
on blogofile 0.7.1, and I seek to have a tool that will continue to be able
to build these sites going forward including when Python 2.7 is no longer
maintained.   Blogofile achieved Python 3 support within the 0.8 series,
however my sites don't work with the 0.8 architecture and additionally
it can't currently be installed due to dependencies that are no longer available
on Pypi (textile==2.1.4 for one).

The general idea of Blogofile is amazingly simple and flexible.  This fork
attempts to make it even simpler, keep Python 3 support going, remove
dependencies that are becoming unavailable, and do only what's needed for my
own sites.   Additionally it merges my "blogodev" command that allows one
to keep the development server running while altering files.

Should the mainline of Blogofile become again maintained, I will enthusiastically
port my sites to the new architecture, however for now I really need something
that can continue to build my sites even after Python 2.7 is no longer available.
