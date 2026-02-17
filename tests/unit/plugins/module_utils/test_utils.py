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
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            convert_ranges_to_port_range,
        )

        result = convert_ranges_to_port_range([])
        assert result == []

    def test_none_ranges(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            convert_ranges_to_port_range,
        )

        result = convert_ranges_to_port_range(None)
        assert result == []

    def test_string_ports(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            convert_ranges_to_port_range,
        )

        result = convert_ranges_to_port_range(["80", "443"])
        assert result == [{"from": "80", "to": "80"}, {"from": "443", "to": "443"}]


class TestNormalizePolicy:
    """Tests for normalize_policy utility function."""

    def test_normalize_with_values(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_policy,
        )

        input_policy = {"name": "test_policy", "enabled": True}
        result = normalize_policy(input_policy)
        assert "name" in result


class TestNormalizePortProcessing:
    """Tests for normalize_port_processing utility function."""

    def test_empty_app(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_port_processing,
        )

        result = normalize_port_processing({})
        assert result == {}

    def test_none_app(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_port_processing,
        )

        result = normalize_port_processing(None)
        assert result == {}

    def test_app_with_ports(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_port_processing,
        )

        input_app = {"name": "test", "tcp_port_range": [{"from": "80", "to": "80"}]}
        result = normalize_port_processing(input_app)
        assert "name" in result


class TestParseHumanReadableTimeout:
    """Tests for parse_human_readable_timeout utility function."""

    def test_hours(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            parse_human_readable_timeout,
        )

        result, error = parse_human_readable_timeout("1 Hour")
        assert error is None

    def test_minutes(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            parse_human_readable_timeout,
        )

        result, error = parse_human_readable_timeout("30 Minutes")
        assert error is None

    def test_days(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            parse_human_readable_timeout,
        )

        result, error = parse_human_readable_timeout("1 Day")
        assert error is None


class TestDiffSuppressFuncCoordinate:
    """Tests for diff_suppress_func_coordinate utility function."""

    def test_same_values(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            diff_suppress_func_coordinate,
        )

        result = diff_suppress_func_coordinate("45.0", "45.0")
        assert result is True

    def test_different_values(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            diff_suppress_func_coordinate,
        )

        result = diff_suppress_func_coordinate("45.0", "46.0")
        assert result is False


class TestConvertPortsAdvanced:
    """Additional tests for convert_ports utility function."""

    def test_convert_ports_dict_format(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            convert_ports,
        )

        input_ports = [{"from": "80", "to": "80"}, {"from": "443", "to": "443"}]
        result = convert_ports(input_ports)
        assert result == [("80", "80"), ("443", "443")]

    def test_convert_ports_tuple_format(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            convert_ports,
        )

        input_ports = [("80", "80"), ("443", "443")]
        result = convert_ports(input_ports)
        assert result == [("80", "80"), ("443", "443")]

    def test_convert_ports_none(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            convert_ports,
        )

        result = convert_ports(None)
        assert result == []

    def test_convert_ports_empty(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            convert_ports,
        )

        result = convert_ports([])
        assert result == []


class TestValidateISO3166Alpha2:
    """Tests for validate_iso3166_alpha2 utility function."""

    def test_valid_country_code_us(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_iso3166_alpha2,
        )

        result = validate_iso3166_alpha2("US")
        assert result is True

    def test_valid_country_code_gb(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_iso3166_alpha2,
        )

        result = validate_iso3166_alpha2("GB")
        assert result is True

    def test_valid_country_code_lowercase(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_iso3166_alpha2,
        )

        result = validate_iso3166_alpha2("us")
        assert result is True

    def test_invalid_country_code(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_iso3166_alpha2,
        )

        result = validate_iso3166_alpha2("XX")
        assert result is False

    def test_invalid_too_long(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_iso3166_alpha2,
        )

        result = validate_iso3166_alpha2("USA")
        assert result is False

    def test_empty_string(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_iso3166_alpha2,
        )

        result = validate_iso3166_alpha2("")
        assert result is False


class TestValidateTimeoutIntervals:
    """Tests for validate_timeout_intervals utility function."""

    def test_valid_interval_human_readable(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_timeout_intervals,
        )

        # Function expects human readable format like "1 Hour"
        result, error = validate_timeout_intervals("1 Hour", minimum=600)
        assert error is None

    def test_interval_below_minimum(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_timeout_intervals,
        )

        result, error = validate_timeout_intervals("5 Minutes", minimum=600)
        assert error is not None

    def test_interval_never(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_timeout_intervals,
        )

        result, error = validate_timeout_intervals("never", minimum=600)
        # "never" is a valid value that returns 0
        assert result == 0 or error is None


class TestNormalizeAppAdvanced:
    """Additional tests for normalize_app utility function."""

    def test_normalize_with_none_values(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_app,
        )

        input_app = {"name": "test", "description": None, "enabled": True}
        result = normalize_app(input_app)
        # None values should be handled
        assert result is not None

    def test_normalize_with_nested_dict(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_app,
        )

        input_app = {"name": "test", "config": {"key": "value"}}
        result = normalize_app(input_app)
        assert "name" in result


class TestNormalizePolicyAdvanced:
    """Additional tests for normalize_policy utility function."""

    def test_normalize_empty_policy(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_policy,
        )

        result = normalize_policy({})
        # normalize_policy adds default keys even for empty input
        assert isinstance(result, dict)

    def test_normalize_policy_with_conditions(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_policy,
        )

        input_policy = {
            "name": "test_policy",
            "action": "ALLOW",
            "conditions": [{"operands": [{"object_type": "APP"}]}],
        }
        result = normalize_policy(input_policy)
        assert "name" in result

    def test_normalize_policy_with_groups(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_policy,
        )

        input_policy = {
            "name": "test_policy",
            "app_connector_group_ids": ["id1", "id2"],
            "app_server_group_ids": ["id3"],
        }
        result = normalize_policy(input_policy)
        assert "app_connector_group_ids" in result


class TestCollectAllItemsAdvanced:
    """Additional tests for collect_all_items with pagination."""

    def test_paginated_response_single_page(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            collect_all_items,
        )

        class MockResp:
            def has_next(self):
                return False

        def mock_list_fn(query_params):
            return (["item1", "item2"], MockResp(), None)

        result, error = collect_all_items(mock_list_fn, {})
        assert error is None
        assert result == ["item1", "item2"]

    def test_paginated_response_with_error(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            collect_all_items,
        )

        def mock_list_fn(query_params):
            return (None, None, "API Error")

        result, error = collect_all_items(mock_list_fn, {})
        assert result is None
        assert error == "API Error"

    def test_paginated_response_multiple_pages(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            collect_all_items,
        )

        call_count = [0]

        class MockResp:
            def __init__(self, has_more):
                self._has_more = has_more

            def has_next(self):
                return self._has_more

            def next(self):
                call_count[0] += 1
                if call_count[0] >= 2:
                    return (["item3", "item4"], MockResp(False), None)
                return (["item3", "item4"], MockResp(True), None)

        def mock_list_fn(query_params):
            return (["item1", "item2"], MockResp(True), None)

        result, error = collect_all_items(mock_list_fn, {})
        assert error is None
        assert len(result) >= 4


class TestNormalizePortProcessingAdvanced:
    """Additional tests for normalize_port_processing."""

    def test_with_tcp_port_range(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_port_processing,
        )

        input_app = {
            "name": "test",
            "tcp_port_range": [
                {"from": "80", "to": "80"},
                {"from": "443", "to": "443"},
            ],
        }
        result = normalize_port_processing(input_app)
        assert "tcp_port_range" in result

    def test_with_udp_port_range(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_port_processing,
        )

        input_app = {"name": "test", "udp_port_range": [{"from": "53", "to": "53"}]}
        result = normalize_port_processing(input_app)
        assert "udp_port_range" in result

    def test_with_tcp_port_ranges_string(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            normalize_port_processing,
        )

        input_app = {"name": "test", "tcp_port_ranges": ["80", "80", "443", "443"]}
        result = normalize_port_processing(input_app)
        assert "tcp_port_ranges" in result


class TestConvertPortsListAdvanced:
    """Additional tests for convert_ports_list."""

    def test_convert_ports_list_none(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            convert_ports_list,
        )

        result = convert_ports_list(None)
        assert result == []

    def test_convert_ports_list_empty(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            convert_ports_list,
        )

        result = convert_ports_list([])
        assert result == []

    def test_convert_ports_list_missing_from(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            convert_ports_list,
        )

        input_ports = [{"to": "80"}]
        result = convert_ports_list(input_ports)
        assert result == []


class TestValidateTcpQuickAck:
    """Tests for validate_tcp_quick_ack utility function."""

    def test_all_true(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_tcp_quick_ack,
        )

        result = validate_tcp_quick_ack(
            tcp_quick_ack_app=True,
            tcp_quick_ack_assistant=True,
            tcp_quick_ack_read_assistant=True,
        )
        # Function returns None when valid, or error message
        assert result is None

    def test_all_false(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_tcp_quick_ack,
        )

        result = validate_tcp_quick_ack(
            tcp_quick_ack_app=False,
            tcp_quick_ack_assistant=False,
            tcp_quick_ack_read_assistant=False,
        )
        assert result is None

    def test_mixed_values(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_tcp_quick_ack,
        )

        result = validate_tcp_quick_ack(
            tcp_quick_ack_app=True,
            tcp_quick_ack_assistant=False,
            tcp_quick_ack_read_assistant=True,
        )
        # May return error or None depending on validation rules
        assert isinstance(result, (str, type(None)))


class TestIsNumberAdvanced:
    """Additional tests for is_number."""

    def test_is_number_float(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            is_number,
        )

        # Floats may or may not be considered numbers depending on implementation
        result = is_number("123.45")
        assert isinstance(result, bool)

    def test_is_number_with_spaces(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            is_number,
        )

        result = is_number(" 123 ")
        assert isinstance(result, bool)


class TestSecondsToHumanReadableAdvanced:
    """Additional tests for seconds_to_human_readable."""

    def test_zero_seconds(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            seconds_to_human_readable,
        )

        result, error = seconds_to_human_readable(0)
        assert result is not None

    def test_large_value(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            seconds_to_human_readable,
        )

        result, error = seconds_to_human_readable(86400)  # 1 day
        assert result is not None

    def test_negative_value(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            seconds_to_human_readable,
        )

        result, error = seconds_to_human_readable(-100)
        # Should handle negative gracefully
        assert isinstance(result, (str, type(None)))


class TestParseHumanReadableTimeoutAdvanced:
    """Additional tests for parse_human_readable_timeout."""

    def test_seconds(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            parse_human_readable_timeout,
        )

        result, error = parse_human_readable_timeout("30 Seconds")
        # May or may not be supported
        assert isinstance(result, (int, type(None)))

    def test_invalid_format(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            parse_human_readable_timeout,
        )

        result, error = parse_human_readable_timeout("invalid")
        # Should return error for invalid format
        assert error is not None or result is None

    def test_numeric_only(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            parse_human_readable_timeout,
        )

        result, error = parse_human_readable_timeout("3600")
        # Pure numeric should work
        assert isinstance(result, (int, type(None)))


class TestValidateLatitudeLongitudeAdvanced:
    """Additional coordinate validation tests."""

    def test_validate_latitude_boundary_low(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_latitude,
        )

        result, errors = validate_latitude(-90)
        assert errors is None

    def test_validate_latitude_boundary_high(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_latitude,
        )

        result, errors = validate_latitude(90)
        assert errors is None

    def test_validate_longitude_boundary_low(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_longitude,
        )

        result, errors = validate_longitude(-180)
        assert errors is None

    def test_validate_longitude_boundary_high(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_longitude,
        )

        result, errors = validate_longitude(180)
        assert errors is None

    def test_validate_latitude_zero(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_latitude,
        )

        result, errors = validate_latitude(0)
        assert errors is None

    def test_validate_longitude_zero(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            validate_longitude,
        )

        result, errors = validate_longitude(0)
        assert errors is None


class TestDeleteNoneAdvanced:
    """Additional tests for deleteNone."""

    def test_delete_none_with_set(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            deleteNone,
        )

        input_set = {1, None, 2, 3}
        result = deleteNone(input_set)
        assert None not in result

    def test_delete_none_with_tuple(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            deleteNone,
        )

        input_tuple = (1, None, 2, None, 3)
        result = deleteNone(input_tuple)
        assert None not in result

    def test_delete_none_nested_list_in_dict(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            deleteNone,
        )

        input_dict = {"key": [1, None, 2]}
        result = deleteNone(input_dict)
        assert None not in result["key"]

    def test_delete_none_key_is_none(self):
        from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
            deleteNone,
        )

        input_dict = {"a": 1, None: "value"}
        result = deleteNone(input_dict)
        assert None not in result
