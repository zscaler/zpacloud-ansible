project = "Zscaler Private Access Ansible Collection"
copyright = "2023, Zscaler Inc."
author = "Zscaler"

extensions = [
    "sphinx_rtd_theme",
]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_context = {
    "display_github": True,
    "github_user": "zscaler",
    "github_repo": "zpacloud-ansible",
    "github_version": "master",
    "conf_py_path": "/docs/source/",
}
