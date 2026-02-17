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

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAPRAPortalControllerModule(ModuleTestCase):
    """Unit tests for zpa_pra_portal_controller module."""

    SAMPLE_PORTAL = {
        "id": "216199618143442004",
        "name": "portal.acme.com",
        "description": "portal.acme.com",
        "domain": "portal.acme.com",
        "enabled": True,
        "certificate_id": "216199618143247243",
        "user_notification": "Test notification",
        "user_notification_enabled": True,
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_portal_controller.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_portal(self, mock_client, mocker):
        """Test creating a new PRA Portal."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_portal_controller.collect_all_items",
            return_value=([], None),
        )

        mock_created = MockBox(self.SAMPLE_PORTAL)
        mock_client.pra_portal.add_portal.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="portal.acme.com",
            description="portal.acme.com",
            domain="portal.acme.com",
            enabled=True,
            certificate_id="216199618143247243",
            user_notification="Test notification",
            user_notification_enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_portal_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_portal_controller.main()

        mock_client.pra_portal.add_portal.assert_called_once()
        assert result.value.result["changed"] is True

    def test_update_portal(self, mock_client, mocker):
        """Test updating an existing PRA Portal."""
        existing_portal = dict(self.SAMPLE_PORTAL)
        existing_portal["description"] = "Old description"
        mock_existing = MockBox(existing_portal)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_portal_controller.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_updated = MockBox(self.SAMPLE_PORTAL)
        mock_client.pra_portal.update_portal.return_value = (mock_updated, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="portal.acme.com",
            description="portal.acme.com",
            domain="portal.acme.com",
            enabled=True,
            certificate_id="216199618143247243",
            user_notification="Test notification",
            user_notification_enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_portal_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_portal_controller.main()

        mock_client.pra_portal.update_portal.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_portal(self, mock_client, mocker):
        """Test deleting a PRA Portal."""
        mock_existing = MockBox(self.SAMPLE_PORTAL)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_portal_controller.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.pra_portal.delete_portal.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="portal.acme.com",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_portal_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_portal_controller.main()

        mock_client.pra_portal.delete_portal.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        """Test no change when portal already matches desired state."""
        # Sample portal that matches the args exactly
        identical_portal = {
            "id": "216199618143442004",
            "name": "portal.acme.com",
            "description": "portal.acme.com",
            "domain": "portal.acme.com",
            "enabled": True,
            "certificate_id": "216199618143247243",
            "user_notification": "Test notification",
            "user_notification_enabled": True,
            "microtenant_id": None,
        }
        mock_existing = MockBox(identical_portal)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_portal_controller.collect_all_items",
            return_value=([mock_existing], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="portal.acme.com",
            description="portal.acme.com",
            domain="portal.acme.com",
            enabled=True,
            certificate_id="216199618143247243",
            user_notification="Test notification",
            user_notification_enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_portal_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_portal_controller.main()

        mock_client.pra_portal.add_portal.assert_not_called()
        mock_client.pra_portal.update_portal.assert_not_called()
        assert result.value.result["changed"] is False

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create operation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_portal_controller.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="new_portal.acme.com",
            domain="new_portal.acme.com",
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_portal_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_portal_controller.main()

        mock_client.pra_portal.add_portal.assert_not_called()
        assert result.value.result["changed"] is True

    def test_delete_nonexistent(self, mock_client, mocker):
        """Test deleting a non-existent portal."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_pra_portal_controller.collect_all_items",
            return_value=([], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="nonexistent", state="absent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_portal_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_portal_controller.main()
        assert result.value.result["changed"] is False

    def test_get_portal_by_id(self, mock_client, mocker):
        """Test retrieving portal by ID."""
        mock_client.pra_portal.get_portal.return_value = (
            MockBox(self.SAMPLE_PORTAL),
            None,
            None,
        )
        mock_client.pra_portal.delete_portal.return_value = (None, None, None)
        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143442004",
            name="portal.acme.com",
            state="absent",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_portal_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_portal_controller.main()
        assert result.value.result["changed"] is True

    def test_list_portals_error(self, mock_client, mocker):
        """Test error handling when listing portals."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_pra_portal_controller.collect_all_items",
            return_value=(None, "API Error"),
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="portal.acme.com",
            domain="portal.acme.com",
            state="present",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_portal_controller,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_pra_portal_controller.main()
        assert "error" in result.value.result["msg"].lower()

    def test_create_portal_error(self, mock_client, mocker):
        """Test error handling when creating portal."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_pra_portal_controller.collect_all_items",
            return_value=([], None),
        )
        mock_client.pra_portal.add_portal.return_value = (None, None, "Create failed")
        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="portal.acme.com",
            domain="portal.acme.com",
            state="present",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_portal_controller,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_pra_portal_controller.main()
        assert "error" in result.value.result["msg"].lower()

    def test_delete_portal_error(self, mock_client, mocker):
        """Test error handling when deleting portal."""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_pra_portal_controller.collect_all_items",
            return_value=([MockBox(self.SAMPLE_PORTAL)], None),
        )
        mock_client.pra_portal.delete_portal.return_value = (
            None,
            None,
            "Delete failed",
        )
        set_module_args(
            provider=DEFAULT_PROVIDER, name="portal.acme.com", state="absent"
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_portal_controller,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_pra_portal_controller.main()
        assert "error" in result.value.result["msg"].lower()

    def test_check_mode_delete(self, mock_client, mocker):
        """Test check mode for delete."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_pra_portal_controller.collect_all_items",
            return_value=([MockBox(self.SAMPLE_PORTAL)], None),
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="portal.acme.com",
            state="absent",
            _ansible_check_mode=True,
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_portal_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_portal_controller.main()
        mock_client.pra_portal.delete_portal.assert_not_called()
        assert result.value.result["changed"] is True
