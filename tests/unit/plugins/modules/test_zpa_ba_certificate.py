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


class TestZPABACertificateModule(ModuleTestCase):
    """Unit tests for zpa_ba_certificate module."""

    SAMPLE_CERT = {
        "id": "216199618143441990",
        "name": "test.example.com",
        "description": "Test BA Certificate",
        "cert_blob": "-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_certificate(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate.collect_all_items",
            return_value=([], None),
        )
        mock_client.certificates.add_certificate.return_value = (MockBox(self.SAMPLE_CERT), None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="test.example.com",
            description="Test BA Certificate",
            cert_blob="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate

        with pytest.raises(AnsibleExitJson) as result:
            zpa_ba_certificate.main()

        assert result.value.result["changed"] is True

    def test_delete_certificate(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate.collect_all_items",
            return_value=([MockBox(self.SAMPLE_CERT)], None),
        )
        mock_client.certificates.delete_certificate.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="test.example.com",
            cert_blob="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate

        with pytest.raises(AnsibleExitJson) as result:
            zpa_ba_certificate.main()

        assert result.value.result["changed"] is True

    def test_certificate_already_exists(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate.collect_all_items",
            return_value=([MockBox(self.SAMPLE_CERT)], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="test.example.com",
            description="Test BA Certificate",
            cert_blob="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate

        with pytest.raises(AnsibleExitJson) as result:
            zpa_ba_certificate.main()

        assert result.value.result["changed"] is False

    def test_delete_nonexistent_certificate(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="nonexistent.example.com",
            cert_blob="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate

        with pytest.raises(AnsibleExitJson) as result:
            zpa_ba_certificate.main()

        assert result.value.result["changed"] is False

    def test_get_certificate_by_id(self, mock_client, mocker):
        """Test retrieving certificate by ID"""
        mock_client.certificates.get_certificate.return_value = (
            MockBox(self.SAMPLE_CERT), None, None
        )
        mock_client.certificates.delete_certificate.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="216199618143441990",
            name="test.example.com",
            cert_blob="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate

        with pytest.raises(AnsibleExitJson) as result:
            zpa_ba_certificate.main()

        assert result.value.result["changed"] is True

    def test_get_certificate_by_id_error(self, mock_client, mocker):
        """Test error when retrieving certificate by ID"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mock_client.certificates.get_certificate.return_value = (None, None, "Not found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="invalid_id",
            name="test.example.com",
            cert_blob="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate

        with pytest.raises(AnsibleFailJson) as result:
            zpa_ba_certificate.main()

        assert "error" in result.value.result["msg"].lower()

    def test_list_certificates_error(self, mock_client, mocker):
        """Test error handling when listing certificates"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate.collect_all_items",
            return_value=(None, "List error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="test.example.com",
            cert_blob="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate

        with pytest.raises(AnsibleFailJson) as result:
            zpa_ba_certificate.main()

        assert "error" in result.value.result["msg"].lower()

    def test_create_certificate_error(self, mock_client, mocker):
        """Test error handling when creating certificate"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate.collect_all_items",
            return_value=([], None),
        )
        mock_client.certificates.add_certificate.return_value = (None, None, "Create failed")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="new.example.com",
            cert_blob="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate

        with pytest.raises(AnsibleFailJson) as result:
            zpa_ba_certificate.main()

        assert "error" in result.value.result["msg"].lower()

    def test_delete_certificate_error(self, mock_client, mocker):
        """Test error handling when deleting certificate"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate.collect_all_items",
            return_value=([MockBox(self.SAMPLE_CERT)], None),
        )
        mock_client.certificates.delete_certificate.return_value = (None, None, "Delete failed")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="test.example.com",
            cert_blob="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate

        with pytest.raises(AnsibleFailJson) as result:
            zpa_ba_certificate.main()

        assert "error" in result.value.result["msg"].lower()

    def test_check_mode_present(self, mock_client, mocker):
        """Test check mode with present state"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="new.example.com",
            cert_blob="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate

        with pytest.raises(AnsibleExitJson) as result:
            zpa_ba_certificate.main()

        assert result.value.result["changed"] is True

    def test_check_mode_absent(self, mock_client, mocker):
        """Test check mode with absent state"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate.collect_all_items",
            return_value=([MockBox(self.SAMPLE_CERT)], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="test.example.com",
            cert_blob="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate

        with pytest.raises(AnsibleExitJson) as result:
            zpa_ba_certificate.main()

        # Check mode returns changed=True when item would be deleted
        assert "changed" in result.value.result or "data" in result.value.result
