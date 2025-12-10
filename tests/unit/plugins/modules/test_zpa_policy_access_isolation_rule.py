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


class TestZPAPolicyAccessIsolationRuleModule(ModuleTestCase):
    """Unit tests for zpa_policy_access_isolation_rule module."""

    SAMPLE_RULE = {
        "id": "216199618143441990",
        "name": "Test_Isolation_Rule",
        "description": "Test Isolation Rule",
        "action": "ISOLATE",
        "rule_order": "1",
        "conditions": [],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_rule(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items",
            return_value=([], None),
        )
        mock_client.policies.add_isolation_rule.return_value = (MockBox(self.SAMPLE_RULE), None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Isolation_Rule",
            description="Test Isolation Rule",
            action="ISOLATE",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_isolation_rule.main()

        assert result.value.result["changed"] is True

    def test_delete_rule(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )
        mock_client.policies.delete_rule.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_Isolation_Rule",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_isolation_rule.main()

        assert result.value.result["changed"] is True

    def test_delete_nonexistent_rule(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="NonExistent_Rule",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_isolation_rule.main()

        assert result.value.result["changed"] is False

    def test_update_rule(self, mock_client, mocker):
        existing_rule = dict(self.SAMPLE_RULE)
        existing_rule["description"] = "Old"
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items",
            return_value=([MockBox(existing_rule)], None),
        )
        mock_client.policies.update_isolation_rule.return_value = (MockBox(self.SAMPLE_RULE), None, None)
        set_module_args(provider=DEFAULT_PROVIDER, state="present", name="Test_Isolation_Rule", description="Test Isolation Rule", action="ISOLATE")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_isolation_rule.main()
        assert result.value.result["changed"] is True

    def test_no_change(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, state="present", name="Test_Isolation_Rule", description="Test Isolation Rule", action="ISOLATE")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_isolation_rule.main()
        assert result.value.result["changed"] is False

    def test_get_rule_by_id(self, mock_client, mocker):
        mock_client.policies.get_rule.return_value = (MockBox(self.SAMPLE_RULE), None, None)
        mock_client.policies.delete_rule.return_value = (None, None, None)
        set_module_args(provider=DEFAULT_PROVIDER, id="216199618143441990", name="Test_Isolation_Rule", state="absent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_isolation_rule.main()
        assert result.value.result["changed"] is True

    def test_get_rule_by_id_error(self, mock_client, mocker):
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mock_client.policies.get_rule.return_value = (None, None, "Not found")
        set_module_args(provider=DEFAULT_PROVIDER, id="invalid_id", name="Test", state="absent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleFailJson):
            zpa_policy_access_isolation_rule.main()

    def test_list_rules_error(self, mock_client, mocker):
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mocker.patch("ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items", return_value=(None, "API Error"))
        set_module_args(provider=DEFAULT_PROVIDER, name="Test", action="ISOLATE", state="present")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleFailJson):
            zpa_policy_access_isolation_rule.main()

    def test_create_rule_error(self, mock_client, mocker):
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mocker.patch("ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items", return_value=([], None))
        mock_client.policies.add_isolation_rule.return_value = (None, None, "Create failed")
        set_module_args(provider=DEFAULT_PROVIDER, name="New", action="ISOLATE", state="present")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleFailJson):
            zpa_policy_access_isolation_rule.main()

    def test_delete_rule_error(self, mock_client, mocker):
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mocker.patch("ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items", return_value=([MockBox(self.SAMPLE_RULE)], None))
        mock_client.policies.delete_rule.return_value = (None, None, "Delete failed")
        set_module_args(provider=DEFAULT_PROVIDER, name="Test_Isolation_Rule", state="absent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleFailJson):
            zpa_policy_access_isolation_rule.main()

    def test_check_mode_create(self, mock_client, mocker):
        mocker.patch("ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items", return_value=([], None))
        set_module_args(provider=DEFAULT_PROVIDER, name="New", action="ISOLATE", state="present", _ansible_check_mode=True)
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_isolation_rule.main()
        assert result.value.result["changed"] is True

    def test_check_mode_delete(self, mock_client, mocker):
        mocker.patch("ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items", return_value=([MockBox(self.SAMPLE_RULE)], None))
        set_module_args(provider=DEFAULT_PROVIDER, name="Test_Isolation_Rule", state="absent", _ansible_check_mode=True)
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_isolation_rule.main()
        assert result.value.result["changed"] is True

    def test_with_microtenant_id(self, mock_client, mocker):
        """Test with microtenant_id parameter."""
        mocker.patch("ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items", return_value=([], None))
        mock_client.policies.add_isolation_rule.return_value = (MockBox(self.SAMPLE_RULE), None, None)
        set_module_args(provider=DEFAULT_PROVIDER, state="present", name="Test_Rule", action="ISOLATE", microtenant_id="123456")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_isolation_rule.main()
        assert result.value.result["changed"] is True

    def test_update_rule_error(self, mock_client, mocker):
        """Test error handling when updating rule."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        existing = dict(self.SAMPLE_RULE)
        existing["description"] = "Old"
        mocker.patch("ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items", return_value=([MockBox(existing)], None))
        mock_client.policies.update_isolation_rule.return_value = (None, None, "Update failed")
        set_module_args(provider=DEFAULT_PROVIDER, state="present", name="Test_Isolation_Rule", description="New", action="ISOLATE")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleFailJson):
            zpa_policy_access_isolation_rule.main()

    def test_check_mode_no_change(self, mock_client, mocker):
        """Test check mode when no changes needed."""
        mocker.patch("ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_isolation_rule.collect_all_items", return_value=([MockBox(self.SAMPLE_RULE)], None))
        set_module_args(provider=DEFAULT_PROVIDER, state="present", name="Test_Isolation_Rule", description="Test Isolation Rule", action="ISOLATE", _ansible_check_mode=True)
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_isolation_rule
        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_isolation_rule.main()
        assert result.value.result["changed"] is False
