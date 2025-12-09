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

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAPRAConsoleControllerModule(ModuleTestCase):
    """Unit tests for zpa_pra_console_controller module."""

    SAMPLE_CONSOLE = {
        "id": "216199618143442010",
        "name": "PRA Console",
        "description": "PRA Console",
        "enabled": True,
        "pra_application_id": "216199618143442001",
        "pra_portal_ids": ["216199618143442004"],
        "pra_portals": [{"id": "216199618143442004"}],
        "pra_application": {"id": "216199618143442001"},
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_console_controller.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_console(self, mock_client, mocker):
        """Test creating a new PRA Console."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_console_controller.collect_all_items",
            return_value=([], None),
        )

        mock_created = MockBox(self.SAMPLE_CONSOLE)
        mock_client.pra_console.add_console.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="PRA Console",
            description="PRA Console",
            enabled=True,
            pra_application_id="216199618143442001",
            pra_portal_ids=["216199618143442004"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_console_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_console_controller.main()

        mock_client.pra_console.add_console.assert_called_once()
        assert result.value.result["changed"] is True

    def test_update_console(self, mock_client, mocker):
        """Test updating an existing PRA Console."""
        existing_console = dict(self.SAMPLE_CONSOLE)
        existing_console["description"] = "Old description"
        mock_existing = MockBox(existing_console)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_console_controller.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_updated = MockBox(self.SAMPLE_CONSOLE)
        mock_client.pra_console.update_console.return_value = (mock_updated, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="PRA Console",
            description="PRA Console",
            enabled=True,
            pra_application_id="216199618143442001",
            pra_portal_ids=["216199618143442004"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_console_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_console_controller.main()

        mock_client.pra_console.update_console.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_console(self, mock_client, mocker):
        """Test deleting a PRA Console."""
        mock_existing = MockBox(self.SAMPLE_CONSOLE)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_console_controller.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.pra_console.delete_console.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="PRA Console",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_console_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_console_controller.main()

        mock_client.pra_console.delete_console.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        """Test no change when console already matches desired state."""
        # Sample console that matches the args exactly (with normalized structure)
        identical_console = {
            "id": "216199618143442010",
            "name": "PRA Console",
            "description": "PRA Console",
            "enabled": True,
            "pra_application_id": "216199618143442001",
            "pra_portal_ids": ["216199618143442004"],
            "pra_portals": [{"id": "216199618143442004"}],
            "pra_application": {"id": "216199618143442001"},
            "microtenant_id": None,
            "icon_text": None,
        }
        mock_existing = MockBox(identical_console)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_console_controller.collect_all_items",
            return_value=([mock_existing], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="PRA Console",
            description="PRA Console",
            enabled=True,
            pra_application_id="216199618143442001",
            pra_portal_ids=["216199618143442004"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_console_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_console_controller.main()

        mock_client.pra_console.add_console.assert_not_called()
        mock_client.pra_console.update_console.assert_not_called()
        assert result.value.result["changed"] is False

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create operation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_console_controller.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New Console",
            description="New Console",
            enabled=True,
            pra_application_id="216199618143442001",
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_console_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_console_controller.main()

        mock_client.pra_console.add_console.assert_not_called()
        assert result.value.result["changed"] is True

