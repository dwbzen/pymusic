
import os
import sys

dir_ = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_)
sys.path.insert(0, os.path.abspath(os.path.join(dir_, "..")))

needs_sphinx = "1.3"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.extlinks',
]
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
source_suffix = '.rst'
master_doc = 'index'
project = 'dwbzen'
copyright = u'2021, Donald W Bacon a.k.a DWBZen'
html_title = project
exclude_patterns = ['_build']

extlinks = {
    'user': ('https://github.com/%s', ''),
}

autodoc_member_order = "bysource"
default_role = "obj"

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "display_version": False,
}

html_context = {
    'extra_css_files': [
        '_static/extra.css',
    ],
}

html_static_path = [
    "extra.css",
]

suppress_warnings = ["image.nonlocal_uri"]
