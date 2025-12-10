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


class TestZPACBICertificateModule(ModuleTestCase):
    """Unit tests for zpa_cloud_browser_isolation_certificate module."""

    SAMPLE_CERT = {
        "id": "dfad8a65-1b24-4a97-83e9-a4f1d80139e1",
        "name": "cbi_profile01.acme.com",
        "pem": "-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_cloud_browser_isolation_certificate.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_certificate(self, mock_client):
        """Test creating a new CBI Certificate."""
        mock_client.cbi_certificate.list_cbi_certificates.return_value = ([], None, None)

        mock_created = MockBox(self.SAMPLE_CERT)
        mock_client.cbi_certificate.add_cbi_certificate.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="cbi_profile01.acme.com",
            pem="-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_certificate.main()

        mock_client.cbi_certificate.add_cbi_certificate.assert_called_once()
        assert result.value.result["changed"] is True

    def test_update_certificate(self, mock_client):
        """Test updating an existing CBI Certificate."""
        existing_cert = dict(self.SAMPLE_CERT)
        existing_cert["pem"] = "-----BEGIN CERTIFICATE-----\nOLDCERT...\n-----END CERTIFICATE-----"
        mock_existing = MockBox(existing_cert)
        mock_client.cbi_certificate.list_cbi_certificates.return_value = ([mock_existing], None, None)

        mock_updated = MockBox(self.SAMPLE_CERT)
        mock_client.cbi_certificate.update_cbi_certificate.return_value = (mock_updated, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="cbi_profile01.acme.com",
            pem="-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_certificate.main()

        mock_client.cbi_certificate.update_cbi_certificate.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_certificate(self, mock_client):
        """Test deleting a CBI Certificate."""
        mock_existing = MockBox(self.SAMPLE_CERT)
        mock_client.cbi_certificate.list_cbi_certificates.return_value = ([mock_existing], None, None)
        mock_client.cbi_certificate.delete_cbi_certificate.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="cbi_profile01.acme.com",
            pem="-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_certificate.main()

        mock_client.cbi_certificate.delete_cbi_certificate.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client):
        """Test no change when certificate already matches desired state."""
        mock_existing = MockBox(self.SAMPLE_CERT)
        mock_client.cbi_certificate.list_cbi_certificates.return_value = ([mock_existing], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="cbi_profile01.acme.com",
            pem="-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_certificate.main()

        mock_client.cbi_certificate.add_cbi_certificate.assert_not_called()
        mock_client.cbi_certificate.update_cbi_certificate.assert_not_called()
        assert result.value.result["changed"] is False

    def test_check_mode_create(self, mock_client):
        """Test check mode for create operation."""
        mock_client.cbi_certificate.list_cbi_certificates.return_value = ([], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="new_cert.acme.com",
            pem="-----BEGIN CERTIFICATE-----\nNEW...\n-----END CERTIFICATE-----",
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_certificate.main()

        mock_client.cbi_certificate.add_cbi_certificate.assert_not_called()
        assert result.value.result["changed"] is True

    def test_get_certificate_by_id(self, mock_client):
        """Test retrieving certificate by ID"""
        mock_client.cbi_certificate.get_cbi_certificate.return_value = (
            MockBox(self.SAMPLE_CERT), None, None
        )
        mock_client.cbi_certificate.delete_cbi_certificate.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="dfad8a65-1b24-4a97-83e9-a4f1d80139e1",
            name="cbi_profile01.acme.com",
            pem="-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_certificate.main()

        assert result.value.result["changed"] is True

    def test_get_certificate_by_id_error(self, mock_client):
        """Test error when retrieving certificate by ID"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mock_client.cbi_certificate.get_cbi_certificate.return_value = (None, None, "Not found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="invalid_id",
            name="Test_Cert",
            pem="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_cloud_browser_isolation_certificate.main()

        assert "error" in result.value.result["msg"].lower()

    def test_list_certificates_error(self, mock_client):
        """Test error handling when listing certificates"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mock_client.cbi_certificate.list_cbi_certificates.return_value = (None, None, "List error")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Cert",
            pem="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_cloud_browser_isolation_certificate.main()

        assert "error" in result.value.result["msg"].lower()

    def test_create_certificate_error(self, mock_client):
        """Test error handling when creating certificate"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mock_client.cbi_certificate.list_cbi_certificates.return_value = ([], None, None)
        mock_client.cbi_certificate.add_cbi_certificate.return_value = (None, None, "Create failed")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="New_Cert",
            pem="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_cloud_browser_isolation_certificate.main()

        assert "error" in result.value.result["msg"].lower()

    def test_update_certificate_error(self, mock_client):
        """Test error handling when updating certificate"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        existing = {**self.SAMPLE_CERT, "pem": "OLD_PEM"}
        mock_client.cbi_certificate.list_cbi_certificates.return_value = ([MockBox(existing)], None, None)
        mock_client.cbi_certificate.update_cbi_certificate.return_value = (None, None, "Update failed")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="cbi_profile01.acme.com",
            pem="-----BEGIN CERTIFICATE-----\nNEW...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_cloud_browser_isolation_certificate.main()

        assert "error" in result.value.result["msg"].lower()

    def test_delete_certificate_error(self, mock_client):
        """Test error handling when deleting certificate"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mock_client.cbi_certificate.list_cbi_certificates.return_value = ([MockBox(self.SAMPLE_CERT)], None, None)
        mock_client.cbi_certificate.delete_cbi_certificate.return_value = (None, None, "Delete failed")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="cbi_profile01.acme.com",
            pem="-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_cloud_browser_isolation_certificate.main()

        assert "error" in result.value.result["msg"].lower()
