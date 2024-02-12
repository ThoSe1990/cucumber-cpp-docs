# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import yaml
import os


project = 'SphinxExample'
copyright = '2023, Thomas'
author = 'Thomas'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
  'breathe',
]

breathe_projects = {
  "cucumber-cpp": "./_build/doxygen/xml"
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'display_version': False
}

build_all_docs = os.environ.get("build_all_docs")
pages_root = os.environ.get("pages_root", "")

if build_all_docs is not None:
  current_version = os.environ.get("current_version")

  html_context = {
    'current_version' : current_version,
    'versions' : [],
  }

  # html_context['versions'].append(['latest', pages_root])

  # with open("versions.yaml", "r") as yaml_file:
  #   docs = yaml.safe_load(yaml_file)

  # for version, details in docs.items():
  #   html_context['versions'].append([version, pages_root+'/'+version])