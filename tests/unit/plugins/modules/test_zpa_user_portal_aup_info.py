# -*- coding: utf-8 -*-
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

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


class TestZPAUserPortalAUPInfoModule(ModuleTestCase):
    """Unit tests for zpa_user_portal_aup_info module."""

    SAMPLE_AUP = {
        "id": "216199618143441990",
        "name": "Test_AUP",
        "description": "Test Acceptable Use Policy",
        "enabled": True,
        "aup_content": "Test AUP Content",
        "version": "1",
    }

    SAMPLE_AUP_2 = {
        "id": "216199618143441991",
        "name": "Test_AUP_2",
        "description": "Test Acceptable Use Policy 2",
        "enabled": True,
        "aup_content": "Test AUP Content 2",
        "version": "1",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_aup_by_id(self, mock_client):
        mock_aup = MockBox(self.SAMPLE_AUP)
        mock_client.user_portal_aup.get_user_portal_aup.return_value = (mock_aup, None, None)

        set_module_args(provider=DEFAULT_PROVIDER, id="216199618143441990")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_user_portal_aup_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup_info.main()

        assert result.value.result["changed"] is False

    def test_get_all_aups(self, mock_client, mocker):
        mock_aups = [MockBox(self.SAMPLE_AUP), MockBox(self.SAMPLE_AUP_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup_info.collect_all_items",
            return_value=(mock_aups, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_user_portal_aup_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup_info.main()

        assert result.value.result["changed"] is False

    def test_aup_not_found_by_id(self, mock_client):
        mock_client.user_portal_aup.get_user_portal_aup.return_value = (None, None, "Not Found")

        set_module_args(provider=DEFAULT_PROVIDER, id="999999999999999999")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_user_portal_aup_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_aup_info.main()

        assert "Failed" in result.value.result["msg"] or "not found" in result.value.result["msg"].lower()

    def test_api_error_on_list(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup_info.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_user_portal_aup_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_aup_info.main()

        assert "Error" in result.value.result["msg"]

    def test_get_aup_by_name(self, mock_client, mocker):
        """Test retrieving AUP by name"""
        mock_aups = [MockBox(self.SAMPLE_AUP), MockBox(self.SAMPLE_AUP_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup_info.collect_all_items",
            return_value=(mock_aups, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER, name="Test_AUP")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_user_portal_aup_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["aups"]) == 1

    def test_aup_not_found_by_name(self, mock_client, mocker):
        """Test error when AUP not found by name"""
        mock_aups = [MockBox(self.SAMPLE_AUP)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup_info.collect_all_items",
            return_value=(mock_aups, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent_AUP")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_user_portal_aup_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_aup_info.main()

        assert "not found" in result.value.result["msg"].lower()

    def test_with_microtenant_id(self, mock_client, mocker):
        """Test with microtenant_id parameter"""
        mock_aups = [MockBox(self.SAMPLE_AUP)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup_info.collect_all_items",
            return_value=(mock_aups, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER, microtenant_id="123456")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_user_portal_aup_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup_info.main()

        assert result.value.result["changed"] is False
