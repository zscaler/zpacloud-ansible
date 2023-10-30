# -*- coding: utf-8 -*-

# Copyright: (c) 2023, William Guilherme  (@willguibr)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    # Common configuration for all ZPA services

    # Formatted for Modules
    CREDENTIALS_SET = """
options:
    client_id:
        description: ""
        required: false
        type: str
    client_secret:
        description: ""
        required: false
        type: str
    customer_id:
        description: ""
        required: false
        type: str
    """

    PROVIDER = r"""
options:
    provider:
        description:
            - A dict object containing connection details.
        version_added: 1.0.0
        required: true
        type: dict
        suboptions:
            client_id:
                description: ""
                type: str
                required: true
            client_secret:
                description: ""
                type: str
                required: true
            customer_id:
                description: ""
                type: str
                required: true
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
