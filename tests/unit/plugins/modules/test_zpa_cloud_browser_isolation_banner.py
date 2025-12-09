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

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPACBIBannerModule(ModuleTestCase):
    """Unit tests for zpa_cloud_browser_isolation_banner module."""

    SAMPLE_BANNER = {
        "id": "70132442-25f8-44eb-a5bb-caeaac67c201",
        "name": "Example CBI Banner",
        "banner": True,
        "notification_title": "Heads up!",
        "notification_text": "You have been redirected",
        "primary_color": "#0076BE",
        "text_color": "#FFFFFF",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_cloud_browser_isolation_banner.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_banner(self, mock_client):
        """Test creating a new CBI Banner."""
        mock_client.cbi_banner.list_cbi_banners.return_value = ([], None, None)

        mock_created = MockBox(self.SAMPLE_BANNER)
        mock_client.cbi_banner.add_cbi_banner.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example CBI Banner",
            banner=True,
            notification_title="Heads up!",
            notification_text="You have been redirected",
            primary_color="#0076BE",
            text_color="#FFFFFF",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_banner,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_banner.main()

        mock_client.cbi_banner.add_cbi_banner.assert_called_once()
        assert result.value.result["changed"] is True

    def test_update_banner(self, mock_client):
        """Test updating an existing CBI Banner."""
        existing_banner = dict(self.SAMPLE_BANNER)
        existing_banner["notification_title"] = "Old Title"
        mock_existing = MockBox(existing_banner)
        mock_client.cbi_banner.list_cbi_banners.return_value = ([mock_existing], None, None)

        updated_banner = dict(self.SAMPLE_BANNER)
        updated_banner["notification_title"] = "New Title"
        mock_updated = MockBox(updated_banner)
        mock_client.cbi_banner.update_cbi_banner.return_value = (mock_updated, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example CBI Banner",
            banner=True,
            notification_title="New Title",
            notification_text="You have been redirected",
            primary_color="#0076BE",
            text_color="#FFFFFF",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_banner,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_banner.main()

        mock_client.cbi_banner.update_cbi_banner.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_banner(self, mock_client):
        """Test deleting a CBI Banner."""
        mock_existing = MockBox(self.SAMPLE_BANNER)
        mock_client.cbi_banner.list_cbi_banners.return_value = ([mock_existing], None, None)
        mock_client.cbi_banner.delete_cbi_banner.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example CBI Banner",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_banner,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_banner.main()

        mock_client.cbi_banner.delete_cbi_banner.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client):
        """Test no change when banner already matches desired state."""
        mock_existing = MockBox(self.SAMPLE_BANNER)
        mock_client.cbi_banner.list_cbi_banners.return_value = ([mock_existing], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example CBI Banner",
            banner=True,
            notification_title="Heads up!",
            notification_text="You have been redirected",
            primary_color="#0076BE",
            text_color="#FFFFFF",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_banner,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_banner.main()

        mock_client.cbi_banner.add_cbi_banner.assert_not_called()
        mock_client.cbi_banner.update_cbi_banner.assert_not_called()
        assert result.value.result["changed"] is False

    def test_check_mode_create(self, mock_client):
        """Test check mode for create operation."""
        mock_client.cbi_banner.list_cbi_banners.return_value = ([], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New CBI Banner",
            banner=True,
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_banner,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_banner.main()

        mock_client.cbi_banner.add_cbi_banner.assert_not_called()
        assert result.value.result["changed"] is True
