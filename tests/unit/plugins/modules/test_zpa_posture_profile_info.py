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


class TestZPAPostureProfileInfoModule(ModuleTestCase):
    """Unit tests for zpa_posture_profile_info module."""

    SAMPLE_PROFILE = {
        "id": "216199618143191254",
        "name": "CrowdStrike_ZPA_Pre-ZTA (zscalertwo.net)",
        "posture_udid": "e2538bb9-af91-49bc-98ea-e90bbe048203",
        "zscaler_cloud": "zscalertwo",
        "apply_to_machine_tunnel_enabled": False,
        "crl_check_enabled": False,
    }

    SAMPLE_PROFILE_2 = {
        "id": "216199618143191255",
        "name": "Custom_Posture (zscalertwo.net)",
        "posture_udid": "f3648cc0-bg02-50cd-99fb-f91cce159314",
        "zscaler_cloud": "zscalertwo",
        "apply_to_machine_tunnel_enabled": True,
        "crl_check_enabled": True,
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_posture_profile_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_profile_by_id(self, mock_client):
        """Test fetching a Posture Profile by ID."""
        mock_profile = MockBox(self.SAMPLE_PROFILE)
        mock_client.posture_profiles.get_profile.return_value = (
            mock_profile,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143191254",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_posture_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_posture_profile_info.main()

        mock_client.posture_profiles.get_profile.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["data"]) == 1

    def test_get_profile_by_name(self, mock_client, mocker):
        """Test fetching a Posture Profile by name (with cloud suffix removal)."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_posture_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="CrowdStrike_ZPA_Pre-ZTA",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_posture_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_posture_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 1

    def test_get_all_profiles(self, mock_client, mocker):
        """Test fetching all Posture Profiles."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_posture_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_posture_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_posture_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 2

    def test_profile_not_found_by_id(self, mock_client):
        """Test fetching a non-existent profile by ID."""
        mock_client.posture_profiles.get_profile.return_value = (
            None,
            None,
            "Not Found",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_posture_profile_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_posture_profile_info.main()

        assert "Failed to retrieve Posture Profile ID" in result.value.result["msg"]

    def test_profile_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent profile by name."""
        mock_profiles = [MockBox(self.SAMPLE_PROFILE)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_posture_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Profile",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_posture_profile_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_posture_profile_info.main()

        assert "not found" in result.value.result["msg"]
