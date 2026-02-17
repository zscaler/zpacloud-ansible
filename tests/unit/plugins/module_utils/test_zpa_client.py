# -*- coding: utf-8 -*-
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch
import os
import pytest


def create_mock_module(params_dict):
    """Create a mock module with proper params.get behavior"""
    mock_module = MagicMock()

    def mock_get(key, default=None):
        return params_dict.get(key, default)

    mock_module.params = MagicMock()
    mock_module.params.get = mock_get
    # Also allow direct attribute access for iteration
    for key, value in params_dict.items():
        setattr(mock_module.params, key, value)

    return mock_module


class TestZPAClientHelper:
    """Tests for ZPAClientHelper class"""

    def test_zpa_argument_spec_returns_dict(self):
        """Test that zpa_argument_spec returns a dictionary with expected keys"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        spec = ZPAClientHelper.zpa_argument_spec()

        assert isinstance(spec, dict)
        assert "provider" in spec
        assert spec["provider"]["type"] == "dict"

    def test_zpa_argument_spec_has_legacy_params(self):
        """Test that argument spec includes legacy authentication parameters"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        spec = ZPAClientHelper.zpa_argument_spec()

        # Check top-level legacy params
        assert "zpa_client_id" in spec
        assert "zpa_client_secret" in spec
        assert "zpa_customer_id" in spec
        assert "zpa_cloud" in spec

    def test_zpa_argument_spec_has_oneapi_params(self):
        """Test that argument spec includes OneAPI authentication parameters"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        spec = ZPAClientHelper.zpa_argument_spec()

        # Check top-level OneAPI params
        assert "client_id" in spec
        assert "client_secret" in spec
        assert "private_key" in spec
        assert "vanity_domain" in spec
        assert "customer_id" in spec

    def test_zpa_argument_spec_provider_options(self):
        """Test that provider dict has all expected options"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        spec = ZPAClientHelper.zpa_argument_spec()
        provider_options = spec["provider"]["options"]

        # Legacy params in provider
        assert "zpa_client_id" in provider_options
        assert "zpa_client_secret" in provider_options
        assert "zpa_customer_id" in provider_options
        assert "zpa_cloud" in provider_options

        # OneAPI params in provider
        assert "client_id" in provider_options
        assert "client_secret" in provider_options
        assert "private_key" in provider_options
        assert "vanity_domain" in provider_options
        assert "use_legacy_client" in provider_options

    def test_zpa_argument_spec_cloud_choices(self):
        """Test that cloud parameters have valid choices from CLOUD_CHOICES"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
            CLOUD_CHOICES,
        )

        spec = ZPAClientHelper.zpa_argument_spec()

        assert spec["zpa_cloud"]["choices"] == CLOUD_CHOICES
        assert spec["cloud"]["choices"] == CLOUD_CHOICES

    def test_valid_zpa_cloud_constant(self):
        """Test that VALID_ZPA_CLOUD contains expected values"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            VALID_ZPA_CLOUD,
        )

        expected = frozenset({"PRODUCTION", "BETA", "QA", "QA2", "GOV", "GOVUS", "PREVIEW", "ZPATWO"})
        assert VALID_ZPA_CLOUD == expected

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.OneAPIClient")
    def test_init_oneapi_client_missing_vanity_domain(self, mock_oneapi):
        """Test that missing vanity_domain fails"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_module = create_mock_module({
            "provider": {
                "client_id": "test_id",
                "client_secret": "test_secret",
                "vanity_domain": None,
            },
            "use_legacy_client": False,
        })

        try:
            ZPAClientHelper(mock_module)
        except Exception:
            pass

        assert mock_module.fail_json.called

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.OneAPIClient")
    def test_init_oneapi_client_missing_client_id(self, mock_oneapi):
        """Test that missing client_id fails"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_module = create_mock_module({
            "provider": {
                "client_id": None,
                "client_secret": "test_secret",
                "vanity_domain": "test.zscaler.com",
            },
            "use_legacy_client": False,
        })

        try:
            ZPAClientHelper(mock_module)
        except Exception:
            pass

        assert mock_module.fail_json.called

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.OneAPIClient")
    def test_init_oneapi_client_both_secrets_fails(self, mock_oneapi):
        """Test that providing both client_secret and private_key fails"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_module = create_mock_module({
            "provider": {
                "client_id": "test_id",
                "client_secret": "test_secret",
                "private_key": "test_key",
                "vanity_domain": "test.zscaler.com",
            },
            "use_legacy_client": False,
        })

        try:
            ZPAClientHelper(mock_module)
        except Exception:
            pass

        assert mock_module.fail_json.called

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.LegacyZPAClient")
    def test_init_legacy_client_missing_params(self, mock_legacy):
        """Test that legacy client fails when required params missing"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_module = create_mock_module({
            "provider": {
                "use_legacy_client": True,
                "zpa_client_id": "test_id",
                # Missing zpa_client_secret, zpa_customer_id, zpa_cloud
            },
            "use_legacy_client": True,
        })

        try:
            ZPAClientHelper(mock_module)
        except Exception:
            pass

        assert mock_module.fail_json.called

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.LegacyZPAClient")
    def test_init_legacy_client_invalid_cloud(self, mock_legacy):
        """Test that legacy client fails with invalid cloud environment"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_module = create_mock_module({
            "provider": {
                "use_legacy_client": True,
                "zpa_client_id": "test_id",
                "zpa_client_secret": "test_secret",
                "zpa_customer_id": "test_customer",
                "zpa_cloud": "INVALID_CLOUD",
            },
            "use_legacy_client": True,
        })

        try:
            ZPAClientHelper(mock_module)
        except Exception:
            pass

        assert mock_module.fail_json.called

    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", False)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.ZSCALER_IMPORT_ERROR", "Import error")
    def test_init_fails_without_zscaler_lib(self):
        """Test that initialization fails when zscaler library is not available"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_module = create_mock_module({"provider": {}})

        try:
            ZPAClientHelper(mock_module)
        except Exception:
            pass

        mock_module.fail_json.assert_called()
        # First fail_json call should be about missing zscaler library
        first_call = mock_module.fail_json.call_args_list[0]
        assert "zscaler" in str(first_call).lower()

    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", False)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.VERSION_IMPORT_ERROR", "Version error")
    def test_init_fails_without_version(self):
        """Test that initialization fails when version module is not available"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_module = create_mock_module({"provider": {}})

        try:
            ZPAClientHelper(mock_module)
        except Exception:
            pass

        mock_module.fail_json.assert_called()
        # First fail_json call should be about version
        first_call = mock_module.fail_json.call_args_list[0]
        assert "version" in str(first_call).lower()

    @patch.dict(os.environ, {"ZSCALER_USE_LEGACY_CLIENT": "true"}, clear=False)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.LegacyZPAClient")
    def test_legacy_client_from_env_var(self, mock_legacy):
        """Test that legacy client is used when ZSCALER_USE_LEGACY_CLIENT env var is set"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_module = create_mock_module({
            "provider": None,
            "use_legacy_client": None,
        })

        try:
            ZPAClientHelper(mock_module)
        except Exception:
            pass

        # Should have attempted to use legacy client (and failed due to missing creds)
        assert mock_module.fail_json.called

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.OneAPIClient")
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.ansible_collection_version", "1.0.0")
    def test_init_oneapi_client_success_with_client_secret(self, mock_oneapi):
        """Test successful OneAPI client initialization with client_secret"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_client_instance = MagicMock()
        mock_oneapi.return_value = mock_client_instance

        mock_module = create_mock_module({
            "provider": {
                "client_id": "test_id",
                "client_secret": "test_secret",
                "vanity_domain": "test.zscaler.com",
                "customer_id": "cust123",
            },
            "use_legacy_client": False,
        })

        helper = ZPAClientHelper(mock_module)

        # Should have created OneAPI client
        mock_oneapi.assert_called_once()
        call_args = mock_oneapi.call_args[0][0]
        assert call_args["clientId"] == "test_id"
        assert call_args["clientSecret"] == "test_secret"
        assert call_args["vanityDomain"] == "test.zscaler.com"

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.OneAPIClient")
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.ansible_collection_version", "1.0.0")
    def test_init_oneapi_client_success_with_private_key(self, mock_oneapi):
        """Test successful OneAPI client initialization with private_key"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_client_instance = MagicMock()
        mock_oneapi.return_value = mock_client_instance

        mock_module = create_mock_module({
            "provider": {
                "client_id": "test_id",
                "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
                "vanity_domain": "test.zscaler.com",
            },
            "use_legacy_client": False,
        })

        helper = ZPAClientHelper(mock_module)

        mock_oneapi.assert_called_once()
        call_args = mock_oneapi.call_args[0][0]
        assert call_args["clientId"] == "test_id"
        assert "privateKey" in call_args

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.LegacyZPAClient")
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.ansible_collection_version", "1.0.0")
    def test_init_legacy_client_success(self, mock_legacy):
        """Test successful legacy client initialization"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_client_instance = MagicMock()
        mock_legacy.return_value = mock_client_instance

        mock_module = create_mock_module({
            "provider": {
                "zpa_client_id": "test_id",
                "zpa_client_secret": "test_secret",
                "zpa_customer_id": "test_customer",
                "zpa_cloud": "PRODUCTION",
                "use_legacy_client": True,
            },
            "use_legacy_client": True,
        })

        helper = ZPAClientHelper(mock_module)

        mock_legacy.assert_called_once()
        call_args = mock_legacy.call_args[0][0]
        assert call_args["clientId"] == "test_id"
        assert call_args["clientSecret"] == "test_secret"
        assert call_args["customerId"] == "test_customer"
        assert call_args["cloud"] == "PRODUCTION"

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.OneAPIClient")
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.ansible_collection_version", "1.0.0")
    def test_getattr_delegates_to_zpa_service(self, mock_oneapi):
        """Test that __getattr__ delegates to client's zpa service"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        # Create mock client with zpa attribute
        mock_client_instance = MagicMock()
        mock_zpa_service = MagicMock()
        mock_zpa_service.app_segments = MagicMock()
        mock_client_instance.zpa = mock_zpa_service
        mock_oneapi.return_value = mock_client_instance

        mock_module = create_mock_module({
            "provider": {
                "client_id": "test_id",
                "client_secret": "test_secret",
                "vanity_domain": "test.zscaler.com",
            },
            "use_legacy_client": False,
        })

        helper = ZPAClientHelper(mock_module)

        # Access an attribute - should delegate to zpa service
        result = helper.app_segments
        assert result == mock_zpa_service.app_segments

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.OneAPIClient")
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.ansible_collection_version", "1.0.0")
    def test_cloud_env_added_to_config(self, mock_oneapi):
        """Test that cloud environment is added to config"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_oneapi.return_value = MagicMock()

        mock_module = create_mock_module({
            "provider": {
                "client_id": "test_id",
                "client_secret": "test_secret",
                "vanity_domain": "test.zscaler.com",
                "cloud": "BETA",
            },
            "use_legacy_client": False,
        })

        ZPAClientHelper(mock_module)

        call_args = mock_oneapi.call_args[0][0]
        assert call_args["cloud"] == "beta"  # Should be lowercased

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.OneAPIClient")
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.ansible_collection_version", "1.0.0")
    def test_init_oneapi_missing_secret_and_key(self, mock_oneapi):
        """Test that missing both client_secret and private_key fails"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_module = create_mock_module({
            "provider": {
                "client_id": "test_id",
                "vanity_domain": "test.zscaler.com",
                # No client_secret or private_key
            },
            "use_legacy_client": False,
        })

        try:
            ZPAClientHelper(mock_module)
        except Exception:
            pass

        assert mock_module.fail_json.called
        call_args = str(mock_module.fail_json.call_args)
        assert "client_secret" in call_args or "private_key" in call_args

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.OneAPIClient")
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.ansible_collection_version", "1.0.0")
    def test_microtenant_id_passed_to_config(self, mock_oneapi):
        """Test that microtenant_id is passed to config"""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_oneapi.return_value = MagicMock()

        mock_module = create_mock_module({
            "provider": {
                "client_id": "test_id",
                "client_secret": "test_secret",
                "vanity_domain": "test.zscaler.com",
                "microtenant_id": "micro123",
            },
            "use_legacy_client": False,
        })

        ZPAClientHelper(mock_module)

        call_args = mock_oneapi.call_args[0][0]
        assert call_args["microtenantId"] == "micro123"

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    def test_legacy_params_without_use_legacy_client_fails(self):
        """Test that Legacy params without use_legacy_client fail with helpful message."""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_module = create_mock_module({
            "provider": {
                "use_legacy_client": False,
                "zpa_client_id": "cid",
                "zpa_client_secret": "secret",
                "zpa_customer_id": "cust",
                "zpa_cloud": "PRODUCTION",
            },
            "use_legacy_client": False,
        })
        mock_module.fail_json.side_effect = Exception("fail_json called")

        with pytest.raises(Exception, match="fail_json called"):
            ZPAClientHelper(mock_module)
        call_msg = mock_module.fail_json.call_args[1]["msg"]
        assert "Legacy API" in call_msg
        assert "use_legacy_client" in call_msg.lower()

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    def test_legacy_client_with_oneapi_params_fails(self):
        """Test that use_legacy_client=true with OneAPI params fails (mutually exclusive)."""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_module = create_mock_module({
            "provider": {
                "use_legacy_client": True,
                "zpa_client_id": "cid",
                "zpa_client_secret": "secret",
                "zpa_customer_id": "cust",
                "zpa_cloud": "PRODUCTION",
                "vanity_domain": "test.zscaler.com",
                "client_id": "oid",
                "client_secret": "osecret",
            },
            "use_legacy_client": True,
        })
        mock_module.fail_json.side_effect = Exception("fail_json called")

        with pytest.raises(Exception, match="fail_json called"):
            ZPAClientHelper(mock_module)
        call_msg = mock_module.fail_json.call_args[1]["msg"]
        assert "use_legacy_client" in call_msg.lower()
        assert "OneAPI" in call_msg

    @patch.dict(os.environ, {}, clear=True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_ZSCALER", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.HAS_VERSION", True)
    @patch("ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.OneAPIClient")
    def test_oneapi_cloud_production_ignored(self, mock_oneapi):
        """Test OneAPI ignores Legacy cloud names (PRODUCTION) to avoid URL breakage."""
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
            ZPAClientHelper,
        )

        mock_oneapi.return_value = MagicMock()

        mock_module = create_mock_module({
            "provider": {
                "client_id": "cid",
                "client_secret": "csecret",
                "vanity_domain": "test.zscaler.com",
                "cloud": "PRODUCTION",
            },
            "use_legacy_client": False,
        })

        ZPAClientHelper(mock_module)
        call_args = mock_oneapi.call_args[0][0]
        assert "cloud" not in call_args
