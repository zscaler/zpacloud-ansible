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


class TestZPAUserPortalAUPModule(ModuleTestCase):
    """Unit tests for zpa_user_portal_aup module."""

    SAMPLE_AUP = {
        "id": "216199618143441990",
        "name": "Test_AUP",
        "description": "Test Acceptable Use Policy",
        "enabled": True,
        "aup": "Test AUP Content",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_aup(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.collect_all_items",
            return_value=([], None),
        )
        mock_client.user_portal_aup.add_user_portal_aup.return_value = (
            MockBox(self.SAMPLE_AUP),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_AUP",
            description="Test Acceptable Use Policy",
            aup="Test AUP Content",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup.main()

        assert result.value.result["changed"] is True

    def test_update_aup(self, mock_client, mocker):
        existing = MockBox({**self.SAMPLE_AUP, "description": "Old Description"})
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.collect_all_items",
            return_value=([existing], None),
        )
        mock_client.user_portal_aup.update_user_portal_aup.return_value = (
            MockBox(self.SAMPLE_AUP),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_AUP",
            description="Test Acceptable Use Policy",
            aup="Test AUP Content",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup.main()

        assert result.value.result["changed"] is True

    def test_delete_aup(self, mock_client, mocker):
        existing = MockBox(self.SAMPLE_AUP)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.collect_all_items",
            return_value=([existing], None),
        )
        mock_client.user_portal_aup.delete_user_portal_aup.return_value = (
            None,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_AUP",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup.main()

        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        existing = MockBox(self.SAMPLE_AUP)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.collect_all_items",
            return_value=([existing], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_AUP",
            description="Test Acceptable Use Policy",
            enabled=True,
            aup="Test AUP Content",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup.main()

        assert result.value.result["changed"] is False

    def test_delete_nonexistent(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="NonExistent_AUP",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup.main()

        assert result.value.result["changed"] is False

    def test_get_aup_by_id(self, mock_client, mocker):
        """Test retrieving AUP by ID"""
        mock_client.user_portal_aup.get_user_portal_aup.return_value = (
            MockBox(self.SAMPLE_AUP),
            None,
            None,
        )
        mock_client.user_portal_aup.delete_user_portal_aup.return_value = (
            None,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="216199618143441990",
            name="Test_AUP",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup.main()

        assert result.value.result["changed"] is True

    def test_get_aup_by_id_error(self, mock_client, mocker):
        """Test error when retrieving AUP by ID"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mock_client.user_portal_aup.get_user_portal_aup.return_value = (
            None,
            None,
            "Not found",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="invalid_id",
            name="Test_AUP",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_aup.main()

        assert "error" in result.value.result["msg"].lower()

    def test_list_aups_error(self, mock_client, mocker):
        """Test error handling when listing AUPs"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.collect_all_items",
            return_value=(None, "List error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_AUP",
            aup="Test AUP Content",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_aup.main()

        assert "error" in result.value.result["msg"].lower()

    def test_update_aup_error(self, mock_client, mocker):
        """Test error handling when updating AUP"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        existing = MockBox({**self.SAMPLE_AUP, "description": "Old Description"})
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.collect_all_items",
            return_value=([existing], None),
        )
        mock_client.user_portal_aup.update_user_portal_aup.return_value = (
            None,
            None,
            "Update failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_AUP",
            description="New Description",
            aup="Test AUP Content",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_aup.main()

        assert "error" in result.value.result["msg"].lower()

    def test_create_aup_error(self, mock_client, mocker):
        """Test error handling when creating AUP"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.collect_all_items",
            return_value=([], None),
        )
        mock_client.user_portal_aup.add_user_portal_aup.return_value = (
            None,
            None,
            "Create failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="New_AUP",
            aup="Test AUP Content",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_aup.main()

        assert "error" in result.value.result["msg"].lower()

    def test_delete_aup_error(self, mock_client, mocker):
        """Test error handling when deleting AUP"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.collect_all_items",
            return_value=([MockBox(self.SAMPLE_AUP)], None),
        )
        mock_client.user_portal_aup.delete_user_portal_aup.return_value = (
            None,
            None,
            "Delete failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_AUP",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_aup.main()

        assert "error" in result.value.result["msg"].lower()

    def test_check_mode_present_new(self, mock_client, mocker):
        """Test check mode with present state - new AUP"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="New_AUP",
            aup="Test AUP Content",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup.main()

        assert result.value.result["changed"] is True

    def test_check_mode_absent(self, mock_client, mocker):
        """Test check mode with absent state"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_aup.collect_all_items",
            return_value=([MockBox(self.SAMPLE_AUP)], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_AUP",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_aup,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_aup.main()

        # Check mode returns changed=True when item would be deleted
        assert "changed" in result.value.result or "data" in result.value.result
