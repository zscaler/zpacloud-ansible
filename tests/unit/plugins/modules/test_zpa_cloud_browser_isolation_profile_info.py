# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import os

COLLECTION_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
if COLLECTION_ROOT not in sys.path:
    sys.path.insert(0, COLLECTION_ROOT)

import pytest
from unittest.mock import MagicMock, patch

from tests.unit.plugins.modules.common.utils import (
    set_module_args,
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    DEFAULT_PROVIDER,
)

from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockBox:
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPACBIProfileInfoModule(ModuleTestCase):
    """Unit tests for zpa_cloud_browser_isolation_profile_info module."""

    SAMPLE_PROFILE = {
        "id": "412da7e7-fa92-4fd3-ab74-c8bb6b3eb41c",
        "name": "CBI_Profile_Example",
        "is_default": False,
        "certificate_ids": [],
        "region_ids": [],
        "security_controls": {
            "allow_printing": True,
            "copy_paste": "all",
            "document_viewer": True,
        },
    }

    SAMPLE_PROFILE_2 = {
        "id": "512da7e7-fa92-4fd3-ab74-c8bb6b3eb42d",
        "name": "CBI_Profile_2",
        "is_default": True,
        "certificate_ids": [],
        "region_ids": [],
        "security_controls": {
            "allow_printing": False,
            "copy_paste": "none",
            "document_viewer": False,
        },
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_cloud_browser_isolation_profile_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_profile_by_id(self, mock_client):
        """Test fetching a CBI Profile by ID."""
        mock_profile = MockBox(self.SAMPLE_PROFILE)
        mock_client.cbi_profile.get_cbi_profile.return_value = (mock_profile, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="412da7e7-fa92-4fd3-ab74-c8bb6b3eb41c",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_profile_info.main()

        mock_client.cbi_profile.get_cbi_profile.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 1
        assert result.value.result["profiles"][0]["name"] == "CBI_Profile_Example"

    def test_get_profile_by_name(self, mock_client):
        """Test fetching a CBI Profile by name."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]
        mock_client.cbi_profile.list_cbi_profiles.return_value = (mock_profiles, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="CBI_Profile_Example",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 1
        assert result.value.result["profiles"][0]["name"] == "CBI_Profile_Example"

    def test_get_all_profiles(self, mock_client):
        """Test fetching all CBI Profiles."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]
        mock_client.cbi_profile.list_cbi_profiles.return_value = (mock_profiles, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 2

    def test_api_error_on_get_by_id(self, mock_client):
        """Test handling API error when fetching by ID."""
        mock_client.cbi_profile.get_cbi_profile.return_value = (None, None, "API Error")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="nonexistent-id",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_profile_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_cloud_browser_isolation_profile_info.main()

        assert "Error retrieving profile by ID" in result.value.result["msg"]
