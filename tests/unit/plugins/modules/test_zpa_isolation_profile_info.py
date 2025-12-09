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
        self.id = data.get("id")
        self.name = data.get("name")

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAIsolationProfileInfoModule(ModuleTestCase):
    """Unit tests for zpa_isolation_profile_info module."""

    SAMPLE_PROFILE = {
        "id": "216199618143212401",
        "name": "BD_SA_Profile1",
        "description": "BD_SA_Profile1",
        "enabled": True,
        "isolation_profile_id": "fdeffec0-9f76-4f42-a39b-9233a1cc09c8",
        "isolation_tenant_id": "8ba47504-e249-4f34-a9ca-6a8fd0a3c322",
    }

    SAMPLE_PROFILE_2 = {
        "id": "216199618143212402",
        "name": "ZPA_CBI_Profile",
        "description": "ZPA CBI Profile",
        "enabled": True,
        "isolation_profile_id": "gdeffec0-9f76-4f42-a39b-9233a1cc09c9",
        "isolation_tenant_id": "9ba47504-e249-4f34-a9ca-6a8fd0a3c323",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_isolation_profile_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_profile_by_id(self, mock_client, mocker):
        """Test fetching an Isolation Profile by ID."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_isolation_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143212401",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_isolation_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_isolation_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 1
        assert result.value.result["profiles"][0]["name"] == "BD_SA_Profile1"

    def test_get_profile_by_name(self, mock_client, mocker):
        """Test fetching an Isolation Profile by name."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_isolation_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="ZPA_CBI_Profile",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_isolation_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_isolation_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 1
        assert result.value.result["profiles"][0]["name"] == "ZPA_CBI_Profile"

    def test_get_all_profiles(self, mock_client, mocker):
        """Test fetching all Isolation Profiles."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_isolation_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_isolation_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_isolation_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 2

    def test_profile_not_found_by_id(self, mock_client, mocker):
        """Test fetching a non-existent profile by ID."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_isolation_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_isolation_profile_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_isolation_profile_info.main()

        assert "not found" in result.value.result["msg"]

    def test_profile_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent profile by name."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_isolation_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Profile",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_isolation_profile_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_isolation_profile_info.main()

        assert "not found" in result.value.result["msg"]

