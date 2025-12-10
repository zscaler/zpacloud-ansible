# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch
from tests.unit.plugins.modules.common.utils import (
    set_module_args, AnsibleExitJson, AnsibleFailJson, ModuleTestCase, DEFAULT_PROVIDER,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import ZPAClientHelper

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockBox:
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data


class TestZPABranchConnectorGroupInfoModule(ModuleTestCase):
    SAMPLE_GROUPS = [
        {"id": "123", "name": "Branch_Group01", "enabled": True},
        {"id": "456", "name": "Branch_Group02", "enabled": True},
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_branch_connector_group_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_all_groups(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_branch_connector_group_info.collect_all_items",
            return_value=([MockBox(g) for g in self.SAMPLE_GROUPS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_branch_connector_group_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_branch_connector_group_info.main()
        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 2

    def test_get_group_by_name(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_branch_connector_group_info.collect_all_items",
            return_value=([MockBox(g) for g in self.SAMPLE_GROUPS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="Branch_Group01")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_branch_connector_group_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_branch_connector_group_info.main()
        assert result.value.result["groups"][0]["name"] == "Branch_Group01"

    def test_group_not_found(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_branch_connector_group_info.collect_all_items",
            return_value=([MockBox(g) for g in self.SAMPLE_GROUPS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_branch_connector_group_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_branch_connector_group_info.main()
        assert "Couldn't find" in result.value.result["msg"]

