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
        self.name = data.get("name")
        self.id = data.get("id")

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAPolicyAccessRuleModule(ModuleTestCase):
    """Unit tests for zpa_policy_access_rule module."""

    SAMPLE_RULE = {
        "id": "216196257331291979",
        "name": "Policy Access Rule - Example",
        "description": "Test access rule",
        "action": "ALLOW",
        "rule_order": "1",
        "order": 1,
        "conditions": [],
        "app_connector_group_ids": [],
        "app_server_group_ids": [],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_rule(self, mock_client, mocker):
        """Test creating a new policy access rule."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([], None),
        )

        mock_created = MockBox(self.SAMPLE_RULE)
        mock_client.policies.add_access_rule.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            description="Test access rule",
            action="ALLOW",
            rule_order="1",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        mock_client.policies.add_access_rule.assert_called_once()
        assert result.value.result["changed"] is True

    def test_update_rule(self, mock_client, mocker):
        """Test updating an existing policy access rule."""
        existing_rule = dict(self.SAMPLE_RULE)
        existing_rule["description"] = "Old description"
        mock_existing = MockBox(existing_rule)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_updated = MockBox(self.SAMPLE_RULE)
        mock_client.policies.update_access_rule.return_value = (
            mock_updated,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            description="Test access rule",
            action="ALLOW",
            rule_order="1",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        mock_client.policies.update_access_rule.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_rule(self, mock_client, mocker):
        """Test deleting a policy access rule."""
        mock_existing = MockBox(self.SAMPLE_RULE)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.policies.delete_rule.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        mock_client.policies.delete_rule.assert_called_once()
        assert result.value.result["changed"] is True

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create operation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New Access Rule",
            action="ALLOW",
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        mock_client.policies.add_access_rule.assert_not_called()
        assert result.value.result["changed"] is True

    def test_rule_with_conditions(self, mock_client, mocker):
        """Test creating rule with conditions."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([], None),
        )

        rule_with_conditions = dict(self.SAMPLE_RULE)
        rule_with_conditions["conditions"] = [
            {
                "operator": "OR",
                "operands": [{"object_type": "APP", "lhs": "id", "rhs": "123456"}],
            }
        ]
        mock_created = MockBox(rule_with_conditions)
        mock_client.policies.add_access_rule.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            description="Test access rule",
            action="ALLOW",
            rule_order="1",
            conditions=[
                {
                    "operator": "OR",
                    "operands": [{"object_type": "APP", "lhs": "id", "rhs": "123456"}],
                }
            ],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        mock_client.policies.add_access_rule.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        """Test no change when rule already matches desired state."""
        mock_existing = MockBox(self.SAMPLE_RULE)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([mock_existing], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            description="Test access rule",
            action="ALLOW",
            rule_order="1",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        mock_client.policies.add_access_rule.assert_not_called()
        mock_client.policies.update_access_rule.assert_not_called()
        assert result.value.result["changed"] is False

    def test_get_rule_by_id(self, mock_client, mocker):
        """Test retrieving rule by ID."""
        mock_existing = MockBox(self.SAMPLE_RULE)
        mock_client.policies.get_rule.return_value = (mock_existing, None, None)
        mock_client.policies.delete_rule.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216196257331291979",
            name="Policy Access Rule - Example",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        mock_client.policies.get_rule.assert_called_once()
        assert result.value.result["changed"] is True

    def test_get_rule_by_id_error(self, mock_client, mocker):
        """Test error when retrieving rule by ID."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mock_client.policies.get_rule.return_value = (None, None, "Not found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="invalid_id",
            name="Test Rule",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_rule.main()

        assert "error" in result.value.result["msg"].lower()

    def test_list_rules_error(self, mock_client, mocker):
        """Test error handling when listing rules."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test Rule",
            action="ALLOW",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_rule.main()

        assert "error" in result.value.result["msg"].lower()

    def test_create_rule_error(self, mock_client, mocker):
        """Test error handling when creating rule."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([], None),
        )
        mock_client.policies.add_access_rule.return_value = (
            None,
            None,
            "Create failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New Rule",
            action="ALLOW",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_rule.main()

        assert "error" in result.value.result["msg"].lower()

    def test_update_rule_error(self, mock_client, mocker):
        """Test error handling when updating rule."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        existing_rule = dict(self.SAMPLE_RULE)
        existing_rule["description"] = "Old description"
        mock_existing = MockBox(existing_rule)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([mock_existing], None),
        )
        mock_client.policies.update_access_rule.return_value = (
            None,
            None,
            "Update failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            description="New description",
            action="ALLOW",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_rule.main()

        assert "error" in result.value.result["msg"].lower()

    def test_delete_rule_error(self, mock_client, mocker):
        """Test error handling when deleting rule."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mock_existing = MockBox(self.SAMPLE_RULE)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([mock_existing], None),
        )
        mock_client.policies.delete_rule.return_value = (None, None, "Delete failed")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_rule.main()

        assert "error" in result.value.result["msg"].lower()

    def test_delete_nonexistent_rule(self, mock_client, mocker):
        """Test deleting a non-existent rule."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent Rule",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        assert result.value.result["changed"] is False

    def test_check_mode_delete(self, mock_client, mocker):
        """Test check mode for delete operation."""
        mock_existing = MockBox(self.SAMPLE_RULE)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([mock_existing], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            state="absent",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        mock_client.policies.delete_rule.assert_not_called()
        assert result.value.result["changed"] is True

    def test_reorder_rule(self, mock_client, mocker):
        """Test reordering an existing rule."""
        existing_rule = dict(self.SAMPLE_RULE)
        existing_rule["order"] = 5
        mock_existing = MockBox(existing_rule)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([mock_existing], None),
        )
        mock_client.policies.reorder_rule.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            description="Test access rule",
            action="ALLOW",
            rule_order="1",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        mock_client.policies.reorder_rule.assert_called_once()

    def test_reorder_rule_error(self, mock_client, mocker):
        """Test error handling when reordering rule."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        existing_rule = dict(self.SAMPLE_RULE)
        existing_rule["order"] = 5
        mock_existing = MockBox(existing_rule)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([mock_existing], None),
        )
        mock_client.policies.reorder_rule.return_value = (None, None, "Reorder failed")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            description="Test access rule",
            action="ALLOW",
            rule_order="1",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_rule.main()

        assert "error" in result.value.result["msg"].lower()

    def test_with_microtenant_id(self, mock_client, mocker):
        """Test rule creation with microtenant_id."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([], None),
        )

        mock_created = MockBox(self.SAMPLE_RULE)
        mock_client.policies.add_access_rule.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            action="ALLOW",
            microtenant_id="123456789",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        assert result.value.result["changed"] is True

    def test_with_connector_and_server_groups(self, mock_client, mocker):
        """Test rule creation with connector and server group IDs."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule.collect_all_items",
            return_value=([], None),
        )

        rule_with_groups = dict(self.SAMPLE_RULE)
        rule_with_groups["app_connector_group_ids"] = ["111", "222"]
        rule_with_groups["app_server_group_ids"] = ["333", "444"]
        mock_created = MockBox(rule_with_groups)
        mock_client.policies.add_access_rule.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            action="ALLOW",
            app_connector_group_ids=["111", "222"],
            app_server_group_ids=["333", "444"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule.main()

        assert result.value.result["changed"] is True
