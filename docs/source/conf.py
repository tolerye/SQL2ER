import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme'
]

html_theme = 'sphinx_rtd_theme'
