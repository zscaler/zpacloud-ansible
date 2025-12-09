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
        self.name = data.get("name")
        self.id = data.get("id")

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAPolicyAccessRuleInfoModule(ModuleTestCase):
    """Unit tests for zpa_policy_access_rule_info module."""

    SAMPLE_RULE = {
        "id": "216196257331291979",
        "name": "Policy Access Rule - Example",
        "description": "Test access rule",
        "action": "ALLOW",
        "rule_order": "1",
        "conditions": [],
    }

    SAMPLE_RULE_2 = {
        "id": "216196257331291980",
        "name": "Policy Access Rule 2",
        "description": "Test access rule 2",
        "action": "DENY",
        "rule_order": "2",
        "conditions": [],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_rule_by_id(self, mock_client):
        """Test fetching a policy rule by ID."""
        mock_rule = MockBox(self.SAMPLE_RULE)
        mock_client.policies.get_rule.return_value = (mock_rule, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216196257331291979",
            policy_type="access",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule_info.main()

        mock_client.policies.get_rule.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["policy_rules"]) == 1

    def test_get_rule_by_name(self, mock_client, mocker):
        """Test fetching a policy rule by name."""
        mock_rules = [MockBox(self.SAMPLE_RULE), MockBox(self.SAMPLE_RULE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_info.collect_all_items",
            return_value=(mock_rules, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Access Rule - Example",
            policy_type="access",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["policy_rules"]) == 1

    def test_get_all_rules(self, mock_client, mocker):
        """Test fetching all policy rules."""
        mock_rules = [MockBox(self.SAMPLE_RULE), MockBox(self.SAMPLE_RULE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_info.collect_all_items",
            return_value=(mock_rules, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            policy_type="access",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["policy_rules"]) == 2

    def test_rule_not_found_by_id(self, mock_client):
        """Test fetching a non-existent rule by ID."""
        mock_client.policies.get_rule.return_value = (None, None, "Not Found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
            policy_type="access",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_rule_info.main()

        assert "Failed to retrieve policy rule ID" in result.value.result["msg"]

    def test_rule_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent rule by name."""
        mock_rules = [MockBox(self.SAMPLE_RULE)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_info.collect_all_items",
            return_value=(mock_rules, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Rule",
            policy_type="access",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_rule_info.main()

        assert "not found" in result.value.result["msg"]

    def test_get_timeout_rules(self, mock_client, mocker):
        """Test fetching timeout policy rules."""
        timeout_rule = {
            "id": "123456",
            "name": "Timeout Rule",
            "description": "Test timeout rule",
            "action": "RE_AUTH",
        }
        mock_rules = [MockBox(timeout_rule)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_info.collect_all_items",
            return_value=(mock_rules, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            policy_type="timeout",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["policy_rules"]) == 1

