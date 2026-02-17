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


class TestZPAPolicyAccessForwardingRuleV2Module(ModuleTestCase):
    """Unit tests for zpa_policy_access_forwarding_rule_v2 module."""

    SAMPLE_RULE = {
        "id": "216199618143441990",
        "name": "Test_Forwarding_Rule_V2",
        "description": "Test Forwarding Rule V2",
        "action": "BYPASS",
        "rule_order": "1",
        "conditions": [],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule_v2.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_rule(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=([], None),
        )
        mock_client.policies.add_client_forwarding_rule_v2.return_value = (
            MockBox(self.SAMPLE_RULE),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Forwarding_Rule_V2",
            description="Test Forwarding Rule V2",
            action="BYPASS",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()

        assert result.value.result["changed"] is True

    def test_delete_rule(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )
        mock_client.policies.delete_rule.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_Forwarding_Rule_V2",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()

        assert result.value.result["changed"] is True

    def test_delete_nonexistent_rule(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="NonExistent_Rule",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()

        assert result.value.result["changed"] is False

    def test_update_rule(self, mock_client, mocker):
        """Test updating an existing rule."""
        existing_rule = dict(self.SAMPLE_RULE)
        existing_rule["description"] = "Old description"
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=([MockBox(existing_rule)], None),
        )
        mock_client.policies.update_client_forwarding_rule_v2.return_value = (
            MockBox(self.SAMPLE_RULE),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Forwarding_Rule_V2",
            description="Test Forwarding Rule V2",
            action="BYPASS",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()

        assert result.value.result["changed"] is True

    def test_get_rule_by_id(self, mock_client, mocker):
        """Test retrieving rule by ID."""
        mock_client.policies.get_rule.return_value = (
            MockBox(self.SAMPLE_RULE),
            None,
            None,
        )
        mock_client.policies.delete_rule.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143441990",
            name="Test_Forwarding_Rule_V2",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()

        assert result.value.result["changed"] is True

    def test_get_rule_by_id_error(self, mock_client, mocker):
        """Test error when retrieving rule by ID."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mock_client.policies.get_rule.return_value = (None, None, "Not found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="invalid_id",
            name="Test_Rule",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()

        assert "error" in result.value.result["msg"].lower()

    def test_list_rules_error(self, mock_client, mocker):
        """Test error handling when listing rules."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Rule",
            action="BYPASS",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()

        assert "error" in result.value.result["msg"].lower()

    def test_create_rule_error(self, mock_client, mocker):
        """Test error handling when creating rule."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=([], None),
        )
        mock_client.policies.add_client_forwarding_rule_v2.return_value = (
            None,
            None,
            "Create failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New_Rule",
            action="BYPASS",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()

        assert "error" in result.value.result["msg"].lower()

    def test_delete_rule_error(self, mock_client, mocker):
        """Test error handling when deleting rule."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )
        mock_client.policies.delete_rule.return_value = (None, None, "Delete failed")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Forwarding_Rule_V2",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()

        assert "error" in result.value.result["msg"].lower()

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New_Rule",
            action="BYPASS",
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()

        mock_client.policies.add_client_forwarding_rule_v2.assert_not_called()
        assert result.value.result["changed"] is True

    def test_check_mode_delete(self, mock_client, mocker):
        """Test check mode for delete."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Forwarding_Rule_V2",
            state="absent",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()

        mock_client.policies.delete_rule.assert_not_called()
        assert result.value.result["changed"] is True

    def test_with_microtenant_id(self, mock_client, mocker):
        """Test with microtenant_id parameter."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=([], None),
        )
        mock_client.policies.add_client_forwarding_rule_v2.return_value = (
            MockBox(self.SAMPLE_RULE),
            None,
            None,
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Rule",
            action="BYPASS",
            microtenant_id="123456",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()
        assert result.value.result["changed"] is True

    def test_update_rule_error(self, mock_client, mocker):
        """Test error handling when updating rule."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        existing = dict(self.SAMPLE_RULE)
        existing["description"] = "Old"
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=([MockBox(existing)], None),
        )
        mock_client.policies.update_client_forwarding_rule_v2.return_value = (
            None,
            None,
            "Update failed",
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Forwarding_Rule_V2",
            description="New",
            action="BYPASS",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleFailJson):
            zpa_policy_access_forwarding_rule_v2.main()

    def test_check_mode_no_change(self, mock_client, mocker):
        """Test check mode when no changes needed."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_access_forwarding_rule_v2.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Forwarding_Rule_V2",
            description="Test Forwarding Rule V2",
            action="BYPASS",
            _ansible_check_mode=True,
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_forwarding_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule_v2.main()
        assert result.value.result["changed"] is False
