# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>

#                              MIT License
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re


def deleteNone(_dict):
    """Delete None values recursively from all of the dictionaries, tuples, lists, sets"""
    if isinstance(_dict, dict):
        for key, value in list(_dict.items()):
            if isinstance(value, (list, dict, tuple, set)):
                _dict[key] = deleteNone(value)
            elif value is None or key is None:
                del _dict[key]
    elif isinstance(_dict, (list, set, tuple)):
        _dict = type(_dict)(deleteNone(item) for item in _dict if item is not None)
    return _dict


def remove_cloud_suffix(s: str) -> str:
    reg = re.compile(r"(.*)[\s]+\([a-zA-Z0-9\-_\.]*\)[\s]*$")
    res = reg.sub(r"\1", s)
    return res.strip()


# Function to handle application segment port conversion list
def convert_ports_list(obj_list):
    if obj_list is None:
        return []
    r = []
    for o in obj_list:
        if o.get("from", None) is not None and o.get("to", None) is not None:
            r.append("" + o.get("from"))
            r.append("" + o.get("to"))
    return r


def convert_ports(obj_list):
    if obj_list is None:
        return []
    r = []
    for o in obj_list:
        if o.get("from", None) is not None and o.get("to", None) is not None:
            c = (o.get("from"), o.get("to"))
            r.append(c)
    return r


def convert_bool_to_str(value, true_value="1", false_value="0"):
    """
    Converts a boolean value to its corresponding string representation.

    Args:
        value (bool or str): The value to be converted.
        true_value (str): The string representation for True.
        false_value (str): The string representation for False.

    Returns:
        str: true_value if the value is True, false_value if the value is False, value if it's already a string.
    """
    if isinstance(value, bool):
        return true_value if value else false_value
    return value  # if the value is already a string, return it as-is


def convert_str_to_bool(value, true_value="1", false_value="0"):
    """
    Converts a string representation of a boolean to an actual boolean.

    Args:
        value (str): The value to be converted.
        true_value (str): The string representation for True.
        false_value (str): The string representation for False.

    Returns:
        bool: True if the value is true_value, False if the value is false_value.
    """
    if value == true_value:
        return True
    elif value == false_value:
        return False
    return value  # if the value isn't recognized, return it as-is


def normalize_common_apps(common_apps):
    normalized = common_apps.copy()
    if "appsConfig" in normalized:
        # You can add more normalization logic for each appConfig object here
        for app_config in normalized["appsConfig"]:
            # For now, I'm just normalizing the 'domain' field
            app_config["domain"] = (
                app_config["domain"].lower() if app_config["domain"] else None
            )
    return normalized


def normalize_app(app):
    normalized = app.copy()

    computed_values = [
        "creation_time",
        "modified_by",
        "modified_time",
        "id",
        "config_space",
        "microtenant_name",
        "segment_group_name",
        "server_groups",
        "use_in_dr_mode",
        "is_incomplete_dr_config",
        "inspect_traffic_with_zia",
        "adp_enabled",
        "app_id",
        "ip_anchored",
        "action",
        "control_number",
        "control_rule_json",
        "protocol_type",
        "rules",
        "version",
        "threatlabz_controls",
        "websocket_controls",
        "zs_defined_control_choice",
        "predef_controls_version",
        "incarnation_number",
        "control_type",
        "check_control_deployment_status",
        "controls_facts",
        "lss_app_connector_group",
    ]
    for attr in computed_values:
        normalized.pop(attr, None)

    # Fix: Convert app_connector_groups to app_connector_group_ids
    if "app_connector_groups" in app:
        normalized["app_connector_group_ids"] = [
            group["id"] for group in app["app_connector_groups"]
        ]

    # Fix: Convert clientless_apps to clientless_app_ids
    if "clientless_apps" in app:
        normalized["clientless_app_ids"] = [
            segment["id"] for segment in app["clientless_apps"]
        ]

    if "tcp_keep_alive" in normalized:
        normalized["tcp_keep_alive"] = convert_str_to_bool(normalized["tcp_keep_alive"])

    if "icmp_access_type" in normalized:
        normalized["icmp_access_type"] = normalized["icmp_access_type"] in [
            "PING",
            "PING_TRACEROUTING",
        ]

    if "server_groups" in app:
        normalized["server_group_ids"] = [group["id"] for group in app["server_groups"]]

    if "common_apps_dto" in normalized and normalized["common_apps_dto"]:
        normalized["common_apps_dto"] = normalize_common_apps(
            normalized["common_apps_dto"]
        )

    # Normalizing clientless_app_ids attributes
    if "clientless_app_ids" in normalized:
        for clientless_app in normalized["clientless_app_ids"]:
            for field in [
                "app_id",
                "id",
                "hidden",
                "portal",
                "path",
                "certificate_name",
                "cname",
                "local_domain",
            ]:
                clientless_app.pop(field, None)

    return normalized


def prepare_updated_app(existing_app, app):
    """
    Prepares the updated application data by merging existing_app and app.
    Note: You might need to adjust the merging logic based on your specific requirements.
    """
    updated_app = existing_app.copy()  # Start with a copy of the existing_app data
    for key, value in app.items():
        # Overwrite fields in updated_app with non-None values from app
        if value is not None:
            updated_app[key] = value
    return updated_app


# Function to handle App Connector and Service Edge Group validations
def validate_latitude(val):
    try:
        v = float(val)
        if v < -90 or v > 90:
            return (None, ["latitude must be between -90 and 90"])
    except ValueError:
        return (None, ["latitude value should be a valid float number or not empty"])
    return (None, None)


def validate_longitude(val):
    try:
        v = float(val)
        if v < -180 or v > 180:
            return (None, ["longitude must be between -180 and 180"])
    except ValueError:
        return (None, ["longitude value should be a valid float number or not empty"])
    return (None, None)


def diff_suppress_func_coordinate(old, new):
    try:
        o = round(float(old) * 1000000) / 1000000
        n = round(float(new) * 1000000) / 1000000
        return o == n
    except ValueError:
        return False


def validate_tcp_quick_ack(
    tcp_quick_ack_app, tcp_quick_ack_assistant, tcp_quick_ack_read_assistant
):
    if (
        tcp_quick_ack_app != tcp_quick_ack_assistant
        or tcp_quick_ack_app != tcp_quick_ack_read_assistant
        or tcp_quick_ack_assistant != tcp_quick_ack_read_assistant
    ):
        return "the values of tcpQuickAck related flags need to be consistent"
    return None


# Function to handle all policy type conditions and normalize upstream computed attributes
def map_conditions(conditions_obj):
    result = []

    # Check if conditions_obj is None or not iterable
    if conditions_obj is None or not isinstance(conditions_obj, list):
        return result

    for condition in conditions_obj:
        operands_list = condition.get("operands")
        if operands_list and isinstance(operands_list, list):
            mapped_operands = []
            for op in operands_list:
                mapped_operand = {
                    "objectType": op.get("object_type"),
                    "lhs": op.get("lhs"),
                    "rhs": op.get("rhs"),
                    "id": op.get("id"),
                    "idp_id": op.get("idp_id"),
                    "name": op.get("name"),
                }
                # Filter out None values
                mapped_operand = {
                    k: v for k, v in mapped_operand.items() if v is not None
                }
                mapped_operands.append(mapped_operand)

            mapped_condition = {
                "id": condition.get("id"),
                "negated": condition.get("negated"),
                "operator": condition.get("operator"),
                "operands": mapped_operands,
            }
            # Filter out None values
            mapped_condition = {
                k: v for k, v in mapped_condition.items() if v is not None
            }
            result.append(mapped_condition)

    return result


def normalize_policy(policy):
    normalized = policy.copy()

    # Exclude the computed values from the data
    computed_values = [
        "modified_time",
        "creation_time",
        "modified_by",
        "rule_order",
        "idp_id",
    ]
    for attr in computed_values:
        normalized.pop(attr, None)

    # Normalize action attribute
    if "action" in normalized and normalized["action"] is not None:
        normalized["action"] = normalized["action"].upper()
    elif "action" in normalized and normalized["action"] is None:
        normalized.pop("action", None)  # Remove 'action' key if the value is None

    # Remove IDs from conditions and operands but keep the main policy rule ID
    for condition in normalized.get("conditions", []):
        condition.pop("id", None)  # remove ID from condition
        condition.pop(
            "negated", None
        )  # remove 'negated' as it is deprecated and can cause issues if not used

        for operand in condition.get("operands", []):
            operand.pop("id", None)  # remove ID from operand
            operand.pop("name", None)  # remove name from operand
            operand.pop("idp_id", None)  # remove idp_id from operand

            # Adjust the operand key from "objectType" to "object_type"
            if "objectType" in operand:
                operand["object_type"] = operand.pop("objectType")

    return normalized


# def normalize_policy(policy):
#     normalized = policy.copy()

#     # Exclude the computed values from the data
#     computed_values = [
#         "modified_time",
#         "creation_time",
#         "modified_by",
#         "rule_order",
#         "idp_id",
#     ]
#     for attr in computed_values:
#         normalized.pop(attr, None)

#     # # Normalize action attribute
#     # if "action" in normalized:
#     #     normalized["action"] = normalized["action"].upper()

#     # Normalize action attribute
#     if "action" in normalized and normalized["action"] is not None:
#         normalized["action"] = normalized["action"].upper()
#     elif "action" in normalized and normalized["action"] is None:
#         normalized.pop("action", None)  # Remove 'action' key if the value is None

#     # Remove IDs from conditions and operands but keep the main policy rule ID
#     for condition in normalized.get("conditions", []):
#         condition.pop("id", None)  # remove ID from condition
#         for operand in condition.get("operands", []):
#             operand.pop("id", None)  # remove ID from operand
#             operand.pop("name", None)  # remove name from operand
#             operand.pop("idp_id", None)  # remove idp_id from operand

#             # Adjust the operand key from "objectType" to "object_type"
#             if "objectType" in operand:
#                 operand["object_type"] = operand.pop("objectType")

#     return normalized


def validate_operand(operand, module):
    def lhsWarn(object_type, expected, got, error=None):
        error_msg = (
            "Invalid LHS for '{object_type}'. Expected {expected}, but got '{got}'"
        )
        if error:
            error_msg += f". Error details: {error}"
        return error_msg

    def rhsWarn(object_type, expected, got, error=None):
        error_msg = (
            f"Invalid RHS for '{object_type}'. Expected {expected}, but got '{got}'"
        )
        if error:
            error_msg += f". Error details: {error}"
        return error_msg

    def idpWarn(object_type, expected, got, error=None):
        error_msg = (
            f"Invalid IDP_ID for '{object_type}'. Expected {expected}, but got '{got}'"
        )
        if error:
            error_msg += f". Error details: {error}"
        return error_msg

    object_type = operand.get("object_type", "").upper()
    lhs = operand.get("lhs")
    rhs = operand.get("rhs")
    idp_id = operand.get("idp_id")

    # Validate non-emptiness
    if not object_type or not lhs or not rhs:
        return "Object type, LHS, and RHS cannot be empty or None"

    # Ensure lhs and rhs are strings
    if not isinstance(lhs, str):
        lhs = str(lhs)
    if not isinstance(rhs, str):
        rhs = str(rhs)

    valid_object_types = [
        "APP",
        "APP_GROUP",
        "MACHINE_GRP",
        "EDGE_CONNECTOR_GROUP",
        "POSTURE",
        "TRUSTED_NETWORK",
        "PLATFORM",
        "COUNTRY_CODE",
        "CLIENT_TYPE",
        "SCIM_GROUP",
        "SCIM",
        "SAML",
    ]

    if object_type not in valid_object_types:
        return f"Invalid object type: {object_type}. Supported types are: {', '.join(valid_object_types)}"

    if object_type in ["APP", "APP_GROUP", "MACHINE_GRP", "EDGE_CONNECTOR_GROUP"]:
        if lhs != "id":
            return lhsWarn(object_type, "id", lhs)
        if not rhs:
            return rhsWarn(object_type, "non-empty string", rhs)

    elif object_type in ["POSTURE", "TRUSTED_NETWORK"]:
        if rhs not in ["true", "false"]:
            return rhsWarn(object_type, "one of ['true', 'false']", rhs)

    elif object_type == "PLATFORM":
        if rhs != "true":
            return rhsWarn(object_type, "true", rhs)
        if lhs not in ["linux", "android", "windows", "ios", "mac"]:
            return lhsWarn(
                object_type, "one of ['linux', 'android', 'windows', 'ios', 'mac']", lhs
            )

    elif object_type == "COUNTRY_CODE":
        if rhs != "true":
            return rhsWarn(object_type, "true", rhs)
        if not validate_iso3166_alpha2(lhs):
            return lhsWarn(
                object_type,
                "a valid ISO-3166 Alpha-2 country code",
                lhs,
                "Please visit the following site for reference: https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes",
            )

    elif object_type == "CLIENT_TYPE":
        if lhs != "id":
            return lhsWarn(object_type, "id", lhs)
        valid_client_types = [
            "zpn_client_type_exporter",
            "zpn_client_type_exporter_noauth",
            "zpn_client_type_browser_isolation",
            "zpn_client_type_machine_tunnel",
            "zpn_client_type_ip_anchoring",
            "zpn_client_type_edge_connector",
            "zpn_client_type_zapp",
            "zpn_client_type_slogger",
            "zpn_client_type_zapp_partner",
            "zpn_client_type_branch_connector",
        ]
        if rhs not in valid_client_types:
            return rhsWarn(object_type, f"one of {valid_client_types}", rhs)

    # New validation logic for SCIM_GROUP, SCIM, and SAML
    if object_type in ["SCIM_GROUP", "SCIM", "SAML"]:
        if not lhs:
            return lhsWarn(object_type, "non-empty string", lhs)
        if not rhs:
            return rhsWarn(object_type, "non-empty string", rhs)
        if not idp_id:  # Check if idp_id is empty or None
            return idpWarn(object_type, "non-empty string", idp_id)

        # Specific validation for each object type
        if object_type == "SCIM_GROUP":
            # Add proper check for Identity Provider ID and SCIM Group ID if necessary
            pass  # Placeholder for any additional validation logic needed for SCIM_GROUP

        elif object_type == "SCIM":
            # Add proper check for SCIM Attribute Header ID and SCIM Attribute Value if necessary
            pass  # Placeholder for any additional validation logic needed for SCIM

        elif object_type == "SAML":
            # Add proper check for SAML Attribute ID and SAML Attribute Value if necessary
            pass  # Placeholder for any additional validation logic needed for SAML

    return None


def validate_iso3166_alpha2(country_code):
    """
    Validates if the provided country code is a valid 2-letter ISO3166 Alpha2 code.

    :param country_code: 2-letter country code
    :return: True if valid, False otherwise
    """
    try:
        import pycountry
    except ImportError:
        raise ImportError(
            "The pycountry module is required to validate ISO3166 Alpha2 country codes."
        )

    try:
        country = pycountry.countries.get(alpha_2=country_code)
        return country is not None
    except AttributeError:
        return False


# This validation function supports the App Protection Custom Controls
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def in_list(val, lst):
    return val in lst


def validate_rules(custom_ctl):
    for rule in custom_ctl.get("rules", []):
        rule_type = rule.get("type")
        conditions = rule.get("conditions", [])

        # Common validation functions
        def validate_size_condition(cond):
            if cond.get("lhs") != "SIZE":
                raise ValueError(f"Expected lhs == 'SIZE' for rule type {rule_type}")
            if cond.get("op") not in ["EQ", "LE", "GE"]:
                raise ValueError(
                    f"Invalid op for rule type {rule_type} with lhs == 'SIZE'"
                )
            if not is_number(cond.get("rhs")):
                raise ValueError(
                    f"rhs must be a string number for rule type {rule_type} with lhs == 'SIZE'"
                )

        def validate_value_condition(cond):
            if cond.get("lhs") != "VALUE":
                raise ValueError(f"Expected lhs == 'VALUE' for rule type {rule_type}")
            if cond.get("op") not in ["CONTAINS", "RX", "STARTS_WITH", "ENDS_WITH"]:
                raise ValueError(
                    f"Invalid op for rule type {rule_type} with lhs == 'VALUE'"
                )

        # Validating RESPONSE rules
        if custom_ctl.get("type") == "RESPONSE":
            if rule_type not in ["RESPONSE_HEADERS", "RESPONSE_BODY"]:
                raise ValueError(
                    "When type == RESPONSE, rules.type must be: RESPONSE_HEADERS or RESPONSE_BODY"
                )

            if not rule.get("names"):
                raise ValueError("names must be set for RESPONSE rules")

            for cond in conditions:
                if cond.get("lhs") == "SIZE":
                    validate_size_condition(cond)
                elif cond.get("lhs") == "VALUE":
                    validate_value_condition(cond)
                else:
                    raise ValueError(f"Invalid lhs for rule type {rule_type}")

        # Validating REQUEST rules
        elif custom_ctl.get("type") == "REQUEST":
            for cond in conditions:
                if rule_type in [
                    "REQUEST_HEADERS",
                    "REQUEST_URI",
                    "QUERY_STRING",
                    "REQUEST_COOKIES",
                    "REQUEST_METHOD",
                ]:
                    if rule_type in [
                        "REQUEST_HEADERS",
                        "REQUEST_COOKIES",
                    ] and not rule.get("names"):
                        raise ValueError(f"names must be set for rule type {rule_type}")

                    if cond.get("lhs") == "SIZE":
                        validate_size_condition(cond)
                    elif cond.get("lhs") == "VALUE":
                        validate_value_condition(cond)
                        if rule_type == "REQUEST_METHOD":
                            if cond.get("rhs") not in [
                                "GET",
                                "POST",
                                "PUT",
                                "PATCH",
                                "CONNECT",
                                "HEAD",
                                "OPTIONS",
                                "DELETE",
                                "TRACE",
                            ]:
                                raise ValueError(
                                    f"Invalid rhs for rule type {rule_type} with lhs == 'VALUE'"
                                )
                    else:
                        raise ValueError(f"Invalid lhs for rule type {rule_type}")
                else:
                    raise ValueError(
                        f"Invalid rule type for type == REQUEST: {rule_type}"
                    )
        else:
            raise ValueError(
                "Invalid type value, it should be either RESPONSE or REQUEST"
            )


# Conversion function for Timeout Policy Rule
def parse_human_readable_timeout(input):
    if input.lower() == "never":
        return -1  # Return -1 for 'Never'

    value, unit = 0, ""
    try:
        parts = input.split()
        value = int(parts[0])
        unit = parts[1].lower()
    except (IndexError, ValueError):
        return None, "Error parsing timeout value: '{}'".format(input)

    multipliers = {
        "minute": 60,
        "minutes": 60,
        "hour": 3600,
        "hours": 3600,
        "day": 86400,
        "days": 86400,
    }

    if unit in multipliers:
        return value * multipliers[unit], None
    else:
        return None, "Unsupported time unit: '{}'".format(unit)


def validate_timeout_intervals(input, minimum=600):
    if input is None:
        return None, None  # Return None for both value and error if input is None

    if input.lower() == "never":
        return -1, None  # Special case for "never"

    timeout_in_seconds, error = parse_human_readable_timeout(input)
    if error:
        return None, error
    if timeout_in_seconds < minimum and timeout_in_seconds != -1:
        return None, "Timeout interval must be at least 10 minutes or 'Never'"
    return timeout_in_seconds, None


def seconds_to_human_readable(seconds):
    try:
        sec = int(seconds)
    except ValueError:
        return "", "Failed to parse seconds as integer"

    if sec == -1:
        return "Never", None

    days = sec // 86400
    hours = (sec % 86400) // 3600
    minutes = (sec % 3600) // 60

    if days > 0:
        return "{} Day{}".format(days, "s" if days > 1 else ""), None
    elif hours > 0:
        return "{} Hour{}".format(hours, "s" if hours > 1 else ""), None
    elif minutes > 0:
        return "{} Minute{}".format(minutes, "s" if minutes > 1 else ""), None
    return "{} Second{}".format(sec, "s" if sec != 1 else ""), None
