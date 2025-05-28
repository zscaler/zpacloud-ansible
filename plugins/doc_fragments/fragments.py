# -*- coding: utf-8 -*-

# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>

#                              MIT License
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
    zpa_client_id:
        description:
            - The ZPA API client ID generated from the ZPA console.
            - Required for legacy client authentication when use_legacy_client=true.
        required: false
        type: str
    zpa_client_secret:
        description:
            - The ZPA API client secret generated from the ZPA console.
            - Required for legacy client authentication when use_legacy_client=true.
        required: false
        type: str
    zpa_customer_id:
        description:
            - The ZPA tenant ID found in the Administration Company menu in the ZPA console.
            - Required for legacy client authentication when use_legacy_client=true.
        required: false
        type: str
    zpa_microtenant_id:
        description:
            - The ZPA Microtenant ID found in the Administration Company menu in the ZPA console.
            - Used for legacy client authentication when use_legacy_client=true.
        type: str
        required: false
    zpa_cloud:
        description:
            - The ZPA cloud provisioned for your organization.
            - Required for legacy client authentication when use_legacy_client=true.
        required: false
        type: str
        choices:
            - BETA
            - GOV
            - GOVUS
            - PRODUCTION
            - QA
            - QA2
            - PREVIEW
            - beta
            - production
    use_legacy_client:
        description:
            - Whether to use the legacy Zscaler API client.
            - When true, uses zpa_client_id/zpa_client_secret/zpa_customer_id/zpa_cloud for authentication.
            - When false (default), uses client_id/client_secret/private_key with vanity_domain for OAuth2 authentication.
        required: false
        type: bool
        default: false
    client_id:
        description:
            - The client ID for OAuth2 authentication.
            - Required for OneAPI client authentication when use_legacy_client=false.
        type: str
        required: false
    client_secret:
        description:
            - The client secret for OAuth2 authentication.
            - Used for OneAPI client authentication when use_legacy_client=false and not using private_key.
        type: str
        required: false
    private_key:
        description:
            - The private key for JWT-based OAuth2 authentication.
            - Used for OneAPI client authentication when use_legacy_client=false and not using client_secret.
        type: str
        required: false
    vanity_domain:
        description:
            - The vanity domain provisioned by Zscaler for OAuth2 flows.
            - Required for OneAPI client authentication when use_legacy_client=false.
        type: str
        required: false
    customer_id:
        description:
            - The ZPA tenant ID found in the Administration Company menu in the ZPA console.
            - Used for OneAPI client authentication when use_legacy_client=false.
        type: str
        required: false
    microtenant_id:
        description:
            - The ZPA Microtenant ID found in the Administration Company menu in the ZPA console.
            - Used for OneAPI client authentication when use_legacy_client=false.
        type: str
        required: false
    cloud:
        description:
            - The ZPA cloud provisioned for your organization.
            - Used for OneAPI client authentication when use_legacy_client=false.
        type: str
        required: false
        choices:
            - BETA
            - GOV
            - GOVUS
            - PRODUCTION
            - QA
            - QA2
            - PREVIEW
            - beta
            - production
"""

    PROVIDER = r"""
options:
    provider:
        description:
            - A dict containing authentication credentials.
        type: dict
        required: false
        suboptions:
            zpa_client_id:
                description:
                    - The ZPA API client ID generated from the ZPA console.
                    - Required for legacy client authentication when use_legacy_client=true.
                type: str
                required: false
            zpa_client_secret:
                description:
                    - The ZPA API client secret generated from the ZPA console.
                    - Required for legacy client authentication when use_legacy_client=true.
                type: str
                required: false
            zpa_customer_id:
                description:
                    - The ZPA tenant ID found in the Administration Company menu in the ZPA console.
                    - Required for legacy client authentication when use_legacy_client=true.
                type: str
                required: false
            zpa_microtenant_id:
                description:
                    - The ZPA Microtenant ID found in the Administration Company menu in the ZPA console.
                    - Used for legacy client authentication when use_legacy_client=true.
                type: str
                required: false
            zpa_cloud:
                description:
                    - The ZPA cloud provisioned for your organization.
                    - Required for legacy client authentication when use_legacy_client=true.
                type: str
                required: false
                choices:
                    - BETA
                    - GOV
                    - GOVUS
                    - PRODUCTION
                    - QA
                    - QA2
                    - PREVIEW
                    - beta
                    - production
            use_legacy_client:
                description:
                    - Whether to use the legacy Zscaler API client.
                    - When true, uses zpa_client_id/zpa_client_secret/zpa_customer_id/zpa_cloud for authentication.
                    - When false (default), uses client_id/client_secret/private_key with vanity_domain for OAuth2 authentication.
                type: bool
                required: false
                default: false
            client_id:
                description:
                    - The client ID for OAuth2 authentication.
                    - Required for OneAPI client authentication when use_legacy_client=false.
                type: str
                required: false
            client_secret:
                description:
                    - The client secret for OAuth2 authentication.
                    - Used for OneAPI client authentication when use_legacy_client=false and not using private_key.
                type: str
                required: false
            private_key:
                description:
                    - The private key for JWT-based OAuth2 authentication.
                    - Used for OneAPI client authentication when use_legacy_client=false and not using client_secret.
                type: str
                required: false
            vanity_domain:
                description:
                    - The vanity domain provisioned by Zscaler for OAuth2 flows.
                    - Required for OneAPI client authentication when use_legacy_client=false.
                type: str
                required: false
            customer_id:
                description:
                    - The ZPA tenant ID found in the Administration Company menu in the ZPA console.
                    - Used for OneAPI client authentication when use_legacy_client=false.
                type: str
                required: false
            microtenant_id:
                description:
                    - The ZPA Microtenant ID found in the Administration Company menu in the ZPA console.
                    - Used for OneAPI client authentication when use_legacy_client=false.
                type: str
                required: false
            cloud:
                description:
                    - The ZPA cloud provisioned for your organization.
                    - Used for OneAPI client authentication when use_legacy_client=false.
                type: str
                required: false
                choices:
                    - BETA
                    - GOV
                    - GOVUS
                    - PRODUCTION
                    - QA
                    - QA2
                    - PREVIEW
                    - beta
                    - production
"""

    STATE = r"""
options:
    state:
        description:
            - Specifies the desired state of the resource.
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
            - Specifies the desired state of the resource.
        type: str
        default: present
        choices:
            - present
            - absent
            - enabled
            - disabled
"""

    MODIFIED_STATE = r"""
options:
    state:
        description:
            - Specifies the desired state of the resource.
        type: str
        default: present
        choices:
            - present
"""
