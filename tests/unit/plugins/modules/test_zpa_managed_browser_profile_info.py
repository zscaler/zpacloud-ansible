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


class TestZPAManagedBrowserProfileInfoModule(ModuleTestCase):
    """Unit tests for zpa_managed_browser_profile_info module."""

    SAMPLE_PROFILE = {
        "id": "216199618143442000",
        "name": "Chrome_Profile",
        "description": "Chrome browser profile for corporate access",
        "browser_type": "CHROME",
    }

    SAMPLE_PROFILE_2 = {
        "id": "216199618143442001",
        "name": "Edge_Profile",
        "description": "Edge browser profile",
        "browser_type": "EDGE",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_managed_browser_profile_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_profile_by_id(self, mock_client, mocker):
        """Test fetching a Managed Browser Profile by ID."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_managed_browser_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143442000",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_managed_browser_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_managed_browser_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 1
        assert result.value.result["profiles"][0]["name"] == "Chrome_Profile"

    def test_get_profile_by_name(self, mock_client, mocker):
        """Test fetching a Managed Browser Profile by name."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_managed_browser_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Chrome_Profile",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_managed_browser_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_managed_browser_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 1
        assert result.value.result["profiles"][0]["name"] == "Chrome_Profile"

    def test_get_all_profiles(self, mock_client, mocker):
        """Test fetching all Managed Browser Profiles."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_managed_browser_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_managed_browser_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_managed_browser_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 2

    def test_profile_not_found_by_id(self, mock_client, mocker):
        """Test fetching a non-existent profile by ID."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_managed_browser_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_managed_browser_profile_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_managed_browser_profile_info.main()

        assert "not found" in result.value.result["msg"]

    def test_profile_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent profile by name."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_managed_browser_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Profile",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_managed_browser_profile_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_managed_browser_profile_info.main()

        assert "not found" in result.value.result["msg"]
