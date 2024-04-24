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
            - The ZPA API client ID generated from the ZPA console.
        type: str
        required: true
    client_secret:
        description:
            - The ZPA API client secret generated from the ZPA console.
        type: str
        required: true
    customer_id:
        description:
            - The ZPA tenant ID found in the Administration
            - Company menu in the ZPA console.
            - The ZPA tenant ID found in the Administration Company menu in the ZPA console.
        type: str
        required: true
    cloud:
        description:
            - The ZPA cloud provisioned for your organization
        required: true
        type: str
        choices:
            - PRODUCTION
            - BETA
            - QA
            - QA2
            - GOV
            - GOVUS
            - PREVIEW
"""

    PROVIDER = r"""
options:
    provider:
        description:
            - A dict object containing authentication details.
        type: dict
        suboptions:
            client_id:
                description:
                    - The ZPA API client ID generated from the ZPA console.
                type: str
                required: true
            client_secret:
                description:
                    - The ZPA API client secret generated from the ZPA console.
                type: str
                required: true
            customer_id:
                description:
                    - The ZPA tenant ID found in the Administration
                    - Company menu in the ZPA console.
                    - The ZPA tenant ID found in the Administration Company menu in the ZPA console.
                type: str
                required: true
            cloud:
                description:
                    - The ZPA cloud provisioned for your organization
                required: true
                type: str
                choices:
                    - PRODUCTION
                    - BETA
                    - QA
                    - QA2
                    - GOV
                    - GOVUS
                    - PREVIEW
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
