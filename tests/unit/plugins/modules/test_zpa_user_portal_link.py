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


class TestZPAUserPortalLinkModule(ModuleTestCase):
    """Unit tests for zpa_user_portal_link module."""

    SAMPLE_LINK = {
        "id": "216199618143441990",
        "name": "Test_Portal_Link",
        "description": "Test Portal Link",
        "enabled": True,
        "link": "https://example.com",
        "protocol": "https://",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_link(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.collect_all_items",
            return_value=([], None),
        )
        mock_client.user_portal_link.add_portal_link.return_value = (
            MockBox(self.SAMPLE_LINK),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Portal_Link",
            description="Test Portal Link",
            link="https://example.com",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_link.main()

        assert result.value.result["changed"] is True

    def test_delete_link(self, mock_client, mocker):
        existing = MockBox(self.SAMPLE_LINK)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.collect_all_items",
            return_value=([existing], None),
        )
        mock_client.user_portal_link.delete_portal_link.return_value = (
            None,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_Portal_Link",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_link.main()

        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        existing = MockBox(self.SAMPLE_LINK)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.collect_all_items",
            return_value=([existing], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Portal_Link",
            description="Test Portal Link",
            enabled=True,
            link="https://example.com",
            protocol="https://",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_link.main()

        assert result.value.result["changed"] is False

    def test_delete_nonexistent(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="NonExistent_Link",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_link.main()

        assert result.value.result["changed"] is False

    def test_get_link_by_id(self, mock_client, mocker):
        """Test retrieving link by ID"""
        mock_client.user_portal_link.get_portal_link.return_value = (
            MockBox(self.SAMPLE_LINK),
            None,
            None,
        )
        mock_client.user_portal_link.delete_portal_link.return_value = (
            None,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="216199618143441990",
            name="Test_Portal_Link",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_link.main()

        assert result.value.result["changed"] is True

    def test_get_link_by_id_error(self, mock_client, mocker):
        """Test error when retrieving link by ID"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mock_client.user_portal_link.get_portal_link.return_value = (
            None,
            None,
            "Not found",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="invalid_id",
            name="Test_Portal_Link",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_link.main()

        assert "error" in result.value.result["msg"].lower()

    def test_list_links_error(self, mock_client, mocker):
        """Test error handling when listing links"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.collect_all_items",
            return_value=(None, "List error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Portal_Link",
            link="https://example.com",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_link.main()

        assert "error" in result.value.result["msg"].lower()

    def test_update_link(self, mock_client, mocker):
        """Test updating an existing link"""
        existing = {**self.SAMPLE_LINK, "description": "Old Description"}
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.collect_all_items",
            return_value=([MockBox(existing)], None),
        )
        mock_client.user_portal_link.update_portal_link.return_value = (
            MockBox({**existing, "description": "New Description"}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Portal_Link",
            description="New Description",
            link="https://example.com",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_link.main()

        assert result.value.result["changed"] is True

    def test_update_link_error(self, mock_client, mocker):
        """Test error handling when updating link"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        existing = {**self.SAMPLE_LINK, "description": "Old Description"}
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.collect_all_items",
            return_value=([MockBox(existing)], None),
        )
        mock_client.user_portal_link.update_portal_link.return_value = (
            None,
            None,
            "Update failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Portal_Link",
            description="New Description",
            link="https://example.com",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_link.main()

        assert "error" in result.value.result["msg"].lower()

    def test_create_link_error(self, mock_client, mocker):
        """Test error handling when creating link"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.collect_all_items",
            return_value=([], None),
        )
        mock_client.user_portal_link.add_portal_link.return_value = (
            None,
            None,
            "Create failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="New_Portal_Link",
            link="https://newlink.com",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_link.main()

        assert "error" in result.value.result["msg"].lower()

    def test_delete_link_error(self, mock_client, mocker):
        """Test error handling when deleting link"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.collect_all_items",
            return_value=([MockBox(self.SAMPLE_LINK)], None),
        )
        mock_client.user_portal_link.delete_portal_link.return_value = (
            None,
            None,
            "Delete failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_Portal_Link",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_link.main()

        assert "error" in result.value.result["msg"].lower()

    def test_check_mode_present_new(self, mock_client, mocker):
        """Test check mode with present state - new link"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="New_Portal_Link",
            link="https://example.com",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_link.main()

        assert result.value.result["changed"] is True

    def test_user_portal_ids_comparison(self, mock_client, mocker):
        """Test comparison of user_portal_link_ids"""
        existing = {
            **self.SAMPLE_LINK,
            "user_portals": [{"id": "portal1"}, {"id": "portal2"}],
        }
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link.collect_all_items",
            return_value=([MockBox(existing)], None),
        )
        mock_client.user_portal_link.update_portal_link.return_value = (
            MockBox(existing),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Portal_Link",
            link="https://example.com",
            user_portal_link_ids=["portal3", "portal4"],
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_user_portal_link,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_link.main()

        # Different portal IDs should trigger update
        assert result.value.result["changed"] is True
