this should eventually grow into a platform showcasing (game/core) loops for learning.

For now, I need a very very basic proof of concept.

- build out @cms/utils/ssg.py so that
    - we render a basic static site to `_site/`
    - index.html should be informed by @cms/templates/index.jinja and for now just render a list of Loops, as defined by `data/loops/*` (each subdir is one loop, with each having a `title` in $subfolder/data.json)
    - each loop has its own sub page, linked on index, for now just rendering title and the diagram ($subfolder/loop.d2), rendered via d2 and ELK to svg and displayed large on the page
    - @cms/templates/styles.css contains the VERY BASIC STYLES (just what's absolutely needed, hard minimalism!!)