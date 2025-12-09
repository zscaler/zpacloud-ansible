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

    def __getitem__(self, key):
        return self._data[key]


class TestZPAPolicyAccessRuleReorderModule(ModuleTestCase):
    """Unit tests for zpa_policy_access_rule_reorder module."""

    SAMPLE_RULES = [
        {"id": "216196257331369420", "name": "Rule 1", "order": 1},
        {"id": "216196257331369421", "name": "Rule 2", "order": 2},
        {"id": "216196257331369422", "name": "Rule 3", "order": 3},
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_reorder.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_reorder_rules(self, mock_client, mocker):
        """Test reordering policy rules."""
        mock_rules = [MockBox(r) for r in self.SAMPLE_RULES]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_reorder.collect_all_items",
            return_value=(mock_rules, None),
        )

        mock_client.policies.bulk_reorder_rules.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            policy_type="access",
            rules=[
                {"id": "216196257331369422", "order": "1"},
                {"id": "216196257331369420", "order": "2"},
                {"id": "216196257331369421", "order": "3"},
            ],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_reorder,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule_reorder.main()

        mock_client.policies.bulk_reorder_rules.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_already_ordered(self, mock_client, mocker):
        """Test no change when rules are already in desired order."""
        mock_rules = [MockBox(r) for r in self.SAMPLE_RULES]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_reorder.collect_all_items",
            return_value=(mock_rules, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            policy_type="access",
            rules=[
                {"id": "216196257331369420", "order": "1"},
                {"id": "216196257331369421", "order": "2"},
                {"id": "216196257331369422", "order": "3"},
            ],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_reorder,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule_reorder.main()

        mock_client.policies.bulk_reorder_rules.assert_not_called()
        assert result.value.result["changed"] is False

    def test_duplicate_order_fails(self, mock_client, mocker):
        """Test that duplicate orders fail validation."""
        mock_rules = [MockBox(r) for r in self.SAMPLE_RULES]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_reorder.collect_all_items",
            return_value=(mock_rules, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            policy_type="access",
            rules=[
                {"id": "216196257331369420", "order": "1"},
                {"id": "216196257331369421", "order": "1"},
                {"id": "216196257331369422", "order": "2"},
            ],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_reorder,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_rule_reorder.main()

        assert "Duplicate order" in result.value.result["msg"]

    def test_zero_order_fails(self, mock_client, mocker):
        """Test that zero order fails validation."""
        mock_rules = [MockBox(r) for r in self.SAMPLE_RULES]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_reorder.collect_all_items",
            return_value=(mock_rules, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            policy_type="access",
            rules=[
                {"id": "216196257331369420", "order": "0"},
                {"id": "216196257331369421", "order": "1"},
                {"id": "216196257331369422", "order": "2"},
            ],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_reorder,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_rule_reorder.main()

        assert "greater than 0" in result.value.result["msg"]

    def test_missing_order_fails(self, mock_client, mocker):
        """Test that missing orders fail validation."""
        mock_rules = [MockBox(r) for r in self.SAMPLE_RULES]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_reorder.collect_all_items",
            return_value=(mock_rules, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            policy_type="access",
            rules=[
                {"id": "216196257331369420", "order": "1"},
                {"id": "216196257331369421", "order": "3"},
                {"id": "216196257331369422", "order": "4"},
            ],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_reorder,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_access_rule_reorder.main()

        assert "Missing rule order" in result.value.result["msg"]

    def test_reorder_timeout_policy(self, mock_client, mocker):
        """Test reordering timeout policy rules."""
        mock_rules = [MockBox(r) for r in self.SAMPLE_RULES]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_rule_reorder.collect_all_items",
            return_value=(mock_rules, None),
        )

        mock_client.policies.bulk_reorder_rules.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            policy_type="timeout",
            rules=[
                {"id": "216196257331369422", "order": "1"},
                {"id": "216196257331369420", "order": "2"},
                {"id": "216196257331369421", "order": "3"},
            ],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_policy_access_rule_reorder,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_rule_reorder.main()

        mock_client.policies.bulk_reorder_rules.assert_called_once()
        assert result.value.result["changed"] is True
