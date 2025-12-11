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


class TestZPAPolicyCredentialAccessRuleModule(ModuleTestCase):
    """Unit tests for zpa_policy_credential_access_rule module."""

    SAMPLE_RULE = {
        "id": "216199618143441990",
        "name": "Test_Credential_Rule",
        "description": "Test Credential Rule",
        "action": "INJECT_CREDENTIALS",
        "rule_order": "1",
        "order": 1,
        "conditions": [],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_rule(self, mock_client, mocker):
        """Test creating a new credential access rule."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([], None),
        )
        mock_created = MockBox(self.SAMPLE_RULE)
        mock_client.policies.add_privileged_credential_rule_v2.return_value = (
            mock_created, None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Credential_Rule",
            description="Test Credential Rule",
            action="INJECT_CREDENTIALS",
            credential={"id": "123456"},
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_credential_access_rule.main()

        assert result.value.result["changed"] is True

    def test_update_rule(self, mock_client, mocker):
        """Test updating an existing rule."""
        existing = dict(self.SAMPLE_RULE)
        existing["description"] = "Old description"
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([MockBox(existing)], None),
        )
        mock_updated = MockBox(self.SAMPLE_RULE)
        mock_client.policies.update_privileged_credential_rule_v2.return_value = (
            mock_updated, None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Credential_Rule",
            description="Test Credential Rule",
            action="INJECT_CREDENTIALS",
            credential={"id": "123456"},
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_credential_access_rule.main()

        assert result.value.result["changed"] is True

    def test_delete_rule(self, mock_client, mocker):
        """Test deleting a rule."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )
        mock_client.policies.delete_rule.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Credential_Rule",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_credential_access_rule.main()

        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        """Test no change when rule matches desired state."""
        # The module requires credential or credential_pool for present state
        # When rule exists and matches, no update should be called
        sample_with_cred = dict(self.SAMPLE_RULE)
        sample_with_cred["credential"] = {"id": "123456"}
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([MockBox(sample_with_cred)], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Credential_Rule",
            description="Test Credential Rule",
            action="INJECT_CREDENTIALS",
            credential={"id": "123456"},
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_credential_access_rule.main()

        # The module will still detect no difference and exit unchanged
        mock_client.policies.update_privileged_credential_rule_v2.assert_not_called()
        mock_client.policies.add_privileged_credential_rule_v2.assert_not_called()

    def test_delete_nonexistent_rule(self, mock_client, mocker):
        """Test deleting a non-existent rule."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Rule",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_credential_access_rule.main()

        assert result.value.result["changed"] is False

    def test_get_rule_by_id(self, mock_client, mocker):
        """Test retrieving rule by ID."""
        mock_client.policies.get_rule.return_value = (MockBox(self.SAMPLE_RULE), None, None)
        mock_client.policies.delete_rule.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143441990",
            name="Test_Credential_Rule",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_credential_access_rule.main()

        assert result.value.result["changed"] is True

    def test_get_rule_by_id_error(self, mock_client, mocker):
        """Test error when retrieving rule by ID."""
        mock_client.policies.get_rule.return_value = (None, None, "Not found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="invalid_id",
            name="Test_Rule",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_credential_access_rule.main()

        assert "error" in result.value.result["msg"].lower()

    def test_list_rules_error(self, mock_client, mocker):
        """Test error handling when listing rules."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Rule",
            credential={"id": "123"},
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_credential_access_rule.main()

        assert "error" in result.value.result["msg"].lower()

    def test_create_rule_error(self, mock_client, mocker):
        """Test error handling when creating rule."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([], None),
        )
        mock_client.policies.add_privileged_credential_rule_v2.return_value = (
            None, None, "Create failed"
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New_Rule",
            credential={"id": "123"},
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_credential_access_rule.main()

        assert "error" in result.value.result["msg"].lower()

    def test_delete_rule_error(self, mock_client, mocker):
        """Test error handling when deleting rule."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )
        mock_client.policies.delete_rule.return_value = (None, None, "Delete failed")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Credential_Rule",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_credential_access_rule.main()

        assert "error" in result.value.result["msg"].lower()

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New_Rule",
            credential={"id": "123"},
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_credential_access_rule.main()

        assert result.value.result["changed"] is True

    def test_check_mode_delete(self, mock_client, mocker):
        """Test check mode for delete."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Credential_Rule",
            state="absent",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_credential_access_rule.main()

        assert result.value.result["changed"] is True

    def test_missing_credential_and_pool(self, mock_client, mocker):
        """Test error when neither credential nor credential_pool provided."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New_Rule",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_credential_access_rule.main()

        assert "credential" in result.value.result["msg"].lower()

    def test_both_credential_and_pool_error(self, mock_client, mocker):
        """Test error when both credential and credential_pool provided."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New_Rule",
            credential={"id": "123"},
            credential_pool={"id": "456"},
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_credential_access_rule.main()

        assert "one of" in result.value.result["msg"].lower()

    def test_with_microtenant_id(self, mock_client, mocker):
        """Test with microtenant_id parameter."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_policy_credential_access_rule.collect_all_items",
            return_value=([], None),
        )
        mock_created = MockBox(self.SAMPLE_RULE)
        mock_client.policies.add_privileged_credential_rule_v2.return_value = (
            mock_created, None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Rule",
            credential={"id": "123"},
            microtenant_id="123456",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_credential_access_rule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_credential_access_rule.main()

        assert result.value.result["changed"] is True
