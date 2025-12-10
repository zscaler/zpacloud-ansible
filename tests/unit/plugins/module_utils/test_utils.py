# -*- coding: utf-8 -*-
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    remove_cloud_suffix,
    collect_all_items,
    normalize_app,
    convert_ports_list,
    convert_bool_to_str,
    convert_str_to_bool,
    validate_latitude,
    validate_longitude,
    is_number,
    in_list,
    seconds_to_human_readable,
)


class TestDeleteNone:
    """Tests for deleteNone utility function."""

    def test_delete_none_from_dict(self):
        input_dict = {"a": 1, "b": None, "c": "value"}
        result = deleteNone(input_dict)
        assert result == {"a": 1, "c": "value"}

    def test_delete_none_from_nested_dict(self):
        input_dict = {"a": 1, "nested": {"b": None, "c": 2}}
        result = deleteNone(input_dict)
        assert result == {"a": 1, "nested": {"c": 2}}

    def test_delete_none_from_list(self):
        input_list = [1, None, 2, None, 3]
        result = deleteNone(input_list)
        assert result == [1, 2, 3]

    def test_delete_none_empty_dict(self):
        result = deleteNone({})
        assert result == {}

    def test_delete_none_empty_list(self):
        result = deleteNone([])
        assert result == []


class TestRemoveCloudSuffix:
    """Tests for remove_cloud_suffix utility function."""

    def test_remove_suffix(self):
        input_str = "My Application (zscalertwo.net)"
        result = remove_cloud_suffix(input_str)
        assert result == "My Application"

    def test_no_suffix(self):
        input_str = "My Application"
        result = remove_cloud_suffix(input_str)
        assert result == "My Application"

    def test_empty_string(self):
        result = remove_cloud_suffix("")
        assert result == ""

    def test_none_input(self):
        result = remove_cloud_suffix(None)
        assert result == ""


class TestCollectAllItems:
    """Tests for collect_all_items utility function."""

    def test_non_paginated_response(self):
        def mock_list_fn(query_params):
            return (["item1", "item2"], None)

        result, error = collect_all_items(mock_list_fn, {})
        assert error is None
        assert result == ["item1", "item2"]

    def test_non_paginated_response_error(self):
        def mock_list_fn(query_params):
            return (None, "API Error")

        result, error = collect_all_items(mock_list_fn, {})
        assert result is None
        assert error == "API Error"

    def test_default_query_params(self):
        captured_params = {}

        def mock_list_fn(query_params):
            captured_params.update(query_params)
            return ([], None)

        collect_all_items(mock_list_fn)
        assert captured_params.get("page_size") == "500"


class TestNormalizeApp:
    """Tests for normalize_app utility function."""

    def test_normalize_empty_dict(self):
        result = normalize_app({})
        assert result == {}

    def test_normalize_with_values(self):
        input_app = {"name": "test", "enabled": True}
        result = normalize_app(input_app)
        assert result["name"] == "test"
        assert result["enabled"] is True


class TestConvertPorts:
    """Tests for convert_ports utility functions."""

    def test_convert_ports_list_with_ports(self):
        input_ports = [{"from": "80", "to": "80"}, {"from": "443", "to": "443"}]
        result = convert_ports_list(input_ports)
        assert result == ["80", "80", "443", "443"]


class TestBoolConversions:
    """Tests for boolean conversion utility functions."""

    def test_convert_bool_to_str_true(self):
        result = convert_bool_to_str(True)
        assert result == "1"

    def test_convert_bool_to_str_false(self):
        result = convert_bool_to_str(False)
        assert result == "0"

    def test_convert_bool_to_str_none(self):
        result = convert_bool_to_str(None)
        assert result is None

    def test_convert_str_to_bool_1(self):
        result = convert_str_to_bool("1")
        assert result is True

    def test_convert_str_to_bool_0(self):
        result = convert_str_to_bool("0")
        assert result is False

    def test_convert_str_to_bool_none(self):
        result = convert_str_to_bool(None)
        assert result is None


class TestValidateCoordinates:
    """Tests for coordinate validation utility functions."""

    def test_validate_latitude_valid(self):
        # Function returns (value, errors) tuple
        result, errors = validate_latitude(45.0)
        assert errors is None

    def test_validate_latitude_invalid(self):
        result, errors = validate_latitude(91)
        assert errors is not None
        assert len(errors) > 0

    def test_validate_longitude_valid(self):
        result, errors = validate_longitude(90.0)
        assert errors is None

    def test_validate_longitude_invalid(self):
        result, errors = validate_longitude(181)
        assert errors is not None
        assert len(errors) > 0


class TestIsNumber:
    """Tests for is_number utility function."""

    def test_is_number_int(self):
        assert is_number("123") is True

    def test_is_number_negative(self):
        assert is_number("-123") is True

    def test_is_number_not_number(self):
        assert is_number("abc") is False

    def test_is_number_empty(self):
        assert is_number("") is False


class TestInList:
    """Tests for in_list utility function."""

    def test_in_list_found(self):
        assert in_list("a", ["a", "b", "c"]) is True

    def test_in_list_not_found(self):
        assert in_list("d", ["a", "b", "c"]) is False

    def test_in_list_empty(self):
        assert in_list("a", []) is False


class TestSecondsToHumanReadable:
    """Tests for seconds_to_human_readable utility function."""

    def test_hours_only(self):
        # Function returns tuple (result, error)
        result, error = seconds_to_human_readable(3600)
        assert "1" in result

    def test_minutes_only(self):
        result, error = seconds_to_human_readable(300)
        assert "5" in result

    def test_complex_time(self):
        result, error = seconds_to_human_readable(3661)
        assert result is not None


class TestConvertRangesToPortRange:
    """Tests for convert_ranges_to_port_range utility function."""

    def test_empty_ranges(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import convert_ranges_to_port_range
        result = convert_ranges_to_port_range([])
        assert result == []

    def test_none_ranges(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import convert_ranges_to_port_range
        result = convert_ranges_to_port_range(None)
        assert result == []

    def test_string_ports(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import convert_ranges_to_port_range
        result = convert_ranges_to_port_range(["80", "443"])
        assert result == [{"from": "80", "to": "80"}, {"from": "443", "to": "443"}]


class TestNormalizePolicy:
    """Tests for normalize_policy utility function."""

    def test_normalize_with_values(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import normalize_policy
        input_policy = {"name": "test_policy", "enabled": True}
        result = normalize_policy(input_policy)
        assert "name" in result


class TestNormalizePortProcessing:
    """Tests for normalize_port_processing utility function."""

    def test_empty_app(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import normalize_port_processing
        result = normalize_port_processing({})
        assert result == {}

    def test_none_app(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import normalize_port_processing
        result = normalize_port_processing(None)
        assert result == {}

    def test_app_with_ports(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import normalize_port_processing
        input_app = {"name": "test", "tcp_port_range": [{"from": "80", "to": "80"}]}
        result = normalize_port_processing(input_app)
        assert "name" in result


class TestParseHumanReadableTimeout:
    """Tests for parse_human_readable_timeout utility function."""

    def test_hours(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import parse_human_readable_timeout
        result, error = parse_human_readable_timeout("1 Hour")
        assert error is None

    def test_minutes(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import parse_human_readable_timeout
        result, error = parse_human_readable_timeout("30 Minutes")
        assert error is None

    def test_days(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import parse_human_readable_timeout
        result, error = parse_human_readable_timeout("1 Day")
        assert error is None


class TestDiffSuppressFuncCoordinate:
    """Tests for diff_suppress_func_coordinate utility function."""

    def test_same_values(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import diff_suppress_func_coordinate
        result = diff_suppress_func_coordinate("45.0", "45.0")
        assert result is True

    def test_different_values(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import diff_suppress_func_coordinate
        result = diff_suppress_func_coordinate("45.0", "46.0")
        assert result is False
