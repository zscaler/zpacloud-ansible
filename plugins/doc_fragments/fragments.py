#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2023, Zscaler, Inc

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    # Standard files documentation fragment
    DOCUMENTATION = r"""
options:
    client_id:
        description:
            - The unique API identifier for the API.
        type: str
        required: true
    client_secret:
        description:
            - Confidential key associated with the client ID.
        type: str
        required: true
    customer_id:
        description:
            - The unique identifier of the ZPA tenant.
        type: str
        required: true
"""
    # Formatted for Modules
    CREDENTIALS_SET = r"""
options:
    client_id:
        description:
            - The unique API identifier for the API.
        type: str
        required: true
    client_secret:
        description:
            - Confidential key associated with the client ID.
        type: str
        required: true
    customer_id:
        description:
            - The unique identifier of the ZPA tenant.
        type: str
        required: true
"""

    PROVIDER = r"""
options:
    provider:
        description:
            - A dict object containing authentication details.
        version_added: 1.0.0
        required: true
        type: dict
        suboptions:
            client_id:
                description:
                    - The unique API identifier for the API.
                type: str
                required: true
            client_secret:
                description:
                    - Confidential key associated with the client ID.
                type: str
                required: true
            customer_id:
                description:
                    - The unique identifier of the ZPA tenant.
                type: str
                required: true
"""

    STATE = r"""
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

    ENABLED_STATE = r"""
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
