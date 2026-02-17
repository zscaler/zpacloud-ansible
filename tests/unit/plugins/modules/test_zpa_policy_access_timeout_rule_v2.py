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


class TestZPAPolicyAccessTimeoutRuleV2Module(ModuleTestCase):
    """Unit tests for zpa_policy_access_timeout_rule_v2 module."""

    SAMPLE_RULE = {
        "id": "216196257331291979",
        "name": "Policy Timeout Rule V2 - Example",
        "description": "Test timeout rule v2",
        "rule_order": "1",
        "order": 1,
        "reauth_idle_timeout": "600",
        "reauth_timeout": "86400",
        "conditions": [],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_timeout_rule_v2.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_timeout_rule_v2(self, mock_client, mocker):
        """Test creating a new policy timeout rule v2."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_timeout_rule_v2.collect_all_items",
            return_value=([], None),
        )
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_timeout_rule_v2.validate_timeout_intervals",
            return_value=("600", None),
        )

        mock_created = MockBox(self.SAMPLE_RULE)
        mock_client.policies.add_timeout_rule_v2.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Timeout Rule V2 - Example",
            description="Test timeout rule v2",
            rule_order="1",
            reauth_idle_timeout="10 minutes",
            reauth_timeout="1 day",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_timeout_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_timeout_rule_v2.main()

        mock_client.policies.add_timeout_rule_v2.assert_called_once()
        assert result.value.result["changed"] is True

    def test_update_timeout_rule_v2(self, mock_client, mocker):
        """Test updating an existing policy timeout rule v2."""
        existing_rule = dict(self.SAMPLE_RULE)
        existing_rule["description"] = "Old description"
        mock_existing = MockBox(existing_rule)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_timeout_rule_v2.collect_all_items",
            return_value=([mock_existing], None),
        )
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_timeout_rule_v2.validate_timeout_intervals",
            return_value=("600", None),
        )

        mock_updated = MockBox(self.SAMPLE_RULE)
        mock_client.policies.update_timeout_rule_v2.return_value = (
            mock_updated,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Timeout Rule V2 - Example",
            description="Test timeout rule v2",
            rule_order="1",
            reauth_idle_timeout="10 minutes",
            reauth_timeout="1 day",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_timeout_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_timeout_rule_v2.main()

        mock_client.policies.update_timeout_rule_v2.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_timeout_rule_v2(self, mock_client, mocker):
        """Test deleting a policy timeout rule v2."""
        mock_existing = MockBox(self.SAMPLE_RULE)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_timeout_rule_v2.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.policies.delete_rule.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Timeout Rule V2 - Example",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_timeout_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_timeout_rule_v2.main()

        mock_client.policies.delete_rule.assert_called_once()
        assert result.value.result["changed"] is True

    def test_check_mode_create_v2(self, mock_client, mocker):
        """Test check mode for create operation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_timeout_rule_v2.collect_all_items",
            return_value=([], None),
        )
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_timeout_rule_v2.validate_timeout_intervals",
            return_value=("600", None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New Timeout Rule V2",
            reauth_idle_timeout="10 minutes",
            reauth_timeout="1 day",
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_timeout_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_timeout_rule_v2.main()

        mock_client.policies.add_timeout_rule_v2.assert_not_called()
        assert result.value.result["changed"] is True

    def test_timeout_rule_v2_with_conditions(self, mock_client, mocker):
        """Test creating timeout rule v2 with conditions."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_timeout_rule_v2.collect_all_items",
            return_value=([], None),
        )
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_timeout_rule_v2.validate_timeout_intervals",
            return_value=("600", None),
        )

        rule_with_conditions = dict(self.SAMPLE_RULE)
        rule_with_conditions["conditions"] = [
            {
                "operator": "OR",
                "operands": [{"object_type": "APP", "values": ["123456"]}],
            }
        ]
        mock_created = MockBox(rule_with_conditions)
        mock_client.policies.add_timeout_rule_v2.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Policy Timeout Rule V2 - Example",
            description="Test timeout rule v2",
            rule_order="1",
            reauth_idle_timeout="10 minutes",
            reauth_timeout="1 day",
            conditions=[
                {
                    "operator": "OR",
                    "operands": [{"object_type": "APP", "values": ["123456"]}],
                }
            ],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_timeout_rule_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_timeout_rule_v2.main()

        mock_client.policies.add_timeout_rule_v2.assert_called_once()
        assert result.value.result["changed"] is True
