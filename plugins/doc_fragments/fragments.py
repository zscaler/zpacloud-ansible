from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    # Standard files documentation fragment
    DOCUMENTATION = """
    """

    STATE = """
options:
    state:
        description:
            - The state.
        type: str
        default: present
        choices:
            - present
            - absent
"""

    ENABLED_STATE = """
options:
    state:
        description:
            - The state.
        type: str
        default: present
        choices:
            - present
            - absent
            - enabled
            - disabled
"""
