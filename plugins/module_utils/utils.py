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
import json


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
    """
    Removes trailing cloud suffix patterns like ' (zscalertwo.net)' from names.
    """
    return re.sub(r"\s*\([a-zA-Z0-9\-_\.]+\)\s*$", "", s or "").strip()


def collect_all_items(list_fn, query_params=None):
    """
    Collects all pages of results from a paginated ZPA SDK list_* method.
    Handles both paginated and non-paginated SDK methods.
    """
    result = list_fn(query_params)

    # Case 1: (items, error) – non-paginated SDK methods
    if isinstance(result, tuple) and len(result) == 2:
        items, err = result
        if err:
            return None, err
        return items or [], None

    # Case 2: (items, resp, error) – paginated SDK methods
    if isinstance(result, tuple) and len(result) == 3:
        items, resp, err = result
        if err:
            return None, err

        all_items = items or []
        while resp and resp.has_next():
            page, resp, err = resp.next()  # ✅ unpack all 3
            if err:
                return None, err
            if page:
                all_items.extend(page)

        return all_items, None

    return None, f"Unexpected return structure from {list_fn.__name__}"


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
        "credentials"
        # "use_in_dr_mode",
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
        "clientless_app_ids",
    ]
    for attr in computed_values:
        normalized.pop(attr, None)

    if "domain_names" in normalized and isinstance(normalized["domain_names"], list):
        normalized["domain_names"].sort()

    # Normalize app_connector_group_ids for proper comparison
    if "app_connector_group_ids" in normalized:
        normalized["app_connector_group_ids"] = sorted(
            normalized["app_connector_group_ids"]
        )

    if "tcp_keep_alive" in normalized:
        normalized["tcp_keep_alive"] = convert_str_to_bool(normalized["tcp_keep_alive"])

    if "icmp_access_type" in normalized:
        normalized["icmp_access_type"] = normalized["icmp_access_type"] in [
            "PING",
            "PING_TRACEROUTING",
        ]

    if "server_groups" in app:
        normalized["server_group_ids"] = [group["id"] for group in app["server_groups"]]

    if "credentials" in app:
        normalized["credential_ids"] = sorted(
            str(c["id"]) for c in app["credentials"] if c.get("id")
        )

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

#     # Convert server's app_connector_groups to app_connector_group_ids
#     if "app_connector_groups" in normalized and isinstance(
#         normalized["app_connector_groups"], list
#     ):
#         normalized["app_connector_group_ids"] = [
#             group["id"] for group in normalized["app_connector_groups"] if "id" in group
#         ]
#         del normalized["app_connector_groups"]

#     # Convert server's app_server_groups to app_server_group_ids
#     if "app_server_groups" in normalized and isinstance(
#         normalized["app_server_groups"], list
#     ):
#         normalized["app_server_group_ids"] = [
#             group["id"] for group in normalized["app_server_groups"] if "id" in group
#         ]
#         del normalized["app_server_groups"]

#     # Normalize action attribute
#     if "action" in normalized and normalized["action"] is not None:
#         normalized["action"] = normalized["action"].upper()
#     elif "action" in normalized and normalized["action"] is None:
#         normalized.pop("action", None)  # Remove 'action' key if the value is None

#     # Remove IDs from conditions and operands but keep the main policy rule ID
#     for condition in normalized.get("conditions", []):
#         condition.pop("id", None)  # remove ID from condition
#         condition.pop("negated", None)  # remove 'negated' as it is deprecated

#         for operand in condition.get("operands", []):
#             operand.pop("id", None)  # remove ID from operand
#             operand.pop("name", None)  # remove name from operand
#             operand.pop("idp_id", None)  # remove idp_id from operand

#             # Adjust the operand key from "objectType" to "object_type"
#             if "objectType" in operand:
#                 operand["object_type"] = operand.pop("objectType")

#     return normalized


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

    # ------------------------------------------------ group ids
    # (keep the object lists around for a moment; we drop them later)
    if "app_connector_groups" in normalized:
        normalized["app_connector_group_ids"] = [
            g.get("id") for g in normalized["app_connector_groups"] if g.get("id")
        ]

    if "app_server_groups" in normalized:
        normalized["app_server_group_ids"] = [
            g.get("id") for g in normalized["app_server_groups"] if g.get("id")
        ]

    # Normalize action attribute
    if "action" in normalized and normalized["action"] is not None:
        normalized["action"] = normalized["action"].upper()
    elif "action" in normalized and normalized["action"] is None:
        normalized.pop("action", None)  # Remove 'action' key if the value is None

    for grp_key, id_key in (
        ("app_connector_groups", "app_connector_group_ids"),
        ("app_server_groups", "app_server_group_ids"),
    ):
        if id_key not in normalized or normalized[id_key] in (None, []):
            objs = normalized.get(grp_key, [])
            if objs:
                normalized[id_key] = [o["id"] for o in objs if "id" in o]

        # Always store as a sorted list (or empty list)
        if normalized.get(id_key) is None:
            normalized[id_key] = []
        else:
            normalized[id_key] = sorted(normalized[id_key])

        # The heavy object lists are no longer needed for comparison
        normalized.pop(grp_key, None)

    # Remove IDs from conditions and operands but keep the main policy rule ID
    for condition in normalized.get("conditions", []):
        condition.pop("id", None)  # remove ID from condition
        condition.pop("negated", None)  # remove 'negated' as it is deprecated

        for operand in condition.get("operands", []):
            operand.pop("id", None)  # remove ID from operand
            operand.pop("name", None)  # remove name from operand
            operand.pop("idp_id", None)  # remove idp_id from operand

            # Adjust the operand key from "objectType" to "object_type"
            if "objectType" in operand:
                operand["object_type"] = operand.pop("objectType")

    return normalized


def validate_operand(operand, module):
    def lhsWarn(object_type, expected, got, error=None):
        error_msg = (
            f"Invalid LHS for '{object_type}'. Expected {expected}, but got '{got}'"
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

    # Ensure lhs and rhs are strings for safety
    if lhs is not None and not isinstance(lhs, str):
        lhs = str(lhs)
    if rhs is not None and not isinstance(rhs, str):
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
        "RISK_FACTOR_TYPE",
        "CHROME_ENTERPRISE",
    ]

    if object_type not in valid_object_types:
        return f"Invalid object type: {object_type}. Supported types are: {', '.join(valid_object_types)}"

    if object_type in [
        "APP",
        "APP_GROUP",
        "MACHINE_GRP",
        "EDGE_CONNECTOR_GROUP",
    ]:
        if not lhs:
            return lhsWarn(object_type, "id", lhs)
        if lhs != "id":
            return lhsWarn(object_type, "id", lhs)
        if not rhs:
            return rhsWarn(object_type, "non-empty string", rhs)

    elif object_type in ["POSTURE", "TRUSTED_NETWORK"]:
        if not lhs:
            return lhsWarn(object_type, "non-empty string", lhs)
        if rhs not in ["true", "false"]:
            return rhsWarn(object_type, "one of ['true', 'false']", rhs)

    elif object_type == "PLATFORM":
        if rhs != "true":
            return rhsWarn(object_type, "true", rhs)
        if lhs not in ["linux", "android", "windows", "ios", "mac"]:
            return lhsWarn(
                object_type, "one of ['linux', 'android', 'windows', 'ios', 'mac']", lhs
            )

    elif object_type == "CHROME_ENTERPRISE":
        # Expect rhs to be 'true' or 'false' (strings)
        if rhs not in ["true", "false"]:
            return rhsWarn(object_type, "one of ['true', 'false']", rhs)
        # lhs can only be 'managed'
        if lhs not in ["managed"]:
            return lhsWarn(object_type, "one of ['managed']", lhs)

    elif object_type == "RISK_FACTOR_TYPE":
        valid_risk_factors = ["UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
        # lhs can only be "ZIA"
        if lhs not in ["ZIA"]:
            return lhsWarn(object_type, "one of ['ZIA']", lhs)
        # rhs must be one of the valid_risk_factors
        if rhs not in valid_risk_factors:
            return rhsWarn(object_type, f"one of {valid_risk_factors}", rhs)

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
        if not lhs:
            return lhsWarn(object_type, "id", lhs)
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

    elif object_type in ["SCIM_GROUP", "SCIM", "SAML"]:
        if not lhs:
            return lhsWarn(object_type, "non-empty string", lhs)
        if not rhs:
            return rhsWarn(object_type, "non-empty string", rhs)
        if not idp_id:
            return idpWarn(object_type, "non-empty string", idp_id)

    return None

# CURRENT WORKING FUNCTION - DO NOT CHANGE
def normalize_policy_v2(policy):
    """
    Canonical-ise an access-rule dict so that the 'conditions' list is stable
    (same order, same key order) and—critically—ignores operand ordering
    inside 'values' lists.  It now also handles raw 3-tuple conditions.
    """
    import copy

    normalized = copy.deepcopy(policy)

    # ------------------------------------------------ metadata
    for k in (
        "modified_time",
        "creation_time",
        "modified_by",
        "policy_type",
        "rule_order",
    ):
        normalized.pop(k, None)

    # ------------------------------------------------ group ids
    # (keep the object lists around for a moment; we drop them later)
    if "app_connector_groups" in normalized:
        normalized["app_connector_group_ids"] = [
            g.get("id") for g in normalized["app_connector_groups"] if g.get("id")
        ]

    if "app_server_groups" in normalized:
        normalized["app_server_group_ids"] = [
            g.get("id") for g in normalized["app_server_groups"] if g.get("id")
        ]

    if "service_edge_groups" in normalized:
        normalized["service_edge_group_ids"] = [
            g.get("id") for g in normalized["service_edge_groups"] if g.get("id")
        ]
    # ------------------------------------------------ credential refs
    if isinstance(normalized.get("credential"), dict):
        normalized["credential_id"] = normalized["credential"].get("id")
        normalized.pop("credential", None)

    if isinstance(normalized.get("credential_pool"), dict):
        normalized["credential_pool_id"] = normalized["credential_pool"].get("id")
        normalized.pop("credential_pool", None)

    if "action" in normalized:
        normalized["action"] = str(normalized["action"]).upper()

    # ------------------------------------------------ ensure ID lists exist, sorted, and objects removed
    for grp_key, id_key in (
        ("app_connector_groups", "app_connector_group_ids"),
        ("app_server_groups", "app_server_group_ids"),
        ("service_edge_groups", "service_edge_group_ids"),
    ):
        if id_key not in normalized or normalized[id_key] in (None, []):
            objs = normalized.get(grp_key, [])
            if objs:
                normalized[id_key] = [o["id"] for o in objs if "id" in o]

        # Always store as a sorted list (or empty list)
        if normalized.get(id_key) is None:
            normalized[id_key] = []
        else:
            normalized[id_key] = sorted(normalized[id_key])

        # The heavy object lists are no longer needed for comparison
        normalized.pop(grp_key, None)

    # ------------------------------------------------ type sets
    VALUE_TYPES = {
        "APP",
        "APP_GROUP",
        "CLIENT_TYPE",
        "MACHINE_GRP",
        "EDGE_CONNECTOR_GROUP",
        "CONSOLE",
        "LOCATION",
        "BRANCH_CONNECTOR_GROUP",
        "CHROME_POSTURE_PROFILE",
    }

    ENTRY_TYPES = {
        "PLATFORM",
        "POSTURE",
        "TRUSTED_NETWORK",
        "SAML",
        "SCIM",
        "SCIM_GROUP",
        "COUNTRY_CODE",
        "RISK_FACTOR_TYPE",
        "CHROME_ENTERPRISE",
    }

    v2_conds = []

    # ------------------------------------------------ iterate user-supplied conditions
    for cond in normalized.get("conditions", []):

        # 0) plain triple ── (obj, lhs, rhs) or (obj, val, None)
        if isinstance(cond, (tuple, list)) and len(cond) == 3:
            obj, lhs, rhs = cond
            obj = obj.upper()

            if obj in ENTRY_TYPES:
                operands = [
                    {
                        "object_type": obj,
                        "entry_values": [{"lhs": lhs, "rhs": rhs}],
                    }
                ]
            else:
                operands = [
                    {
                        "object_type": obj,
                        "values": [str(rhs)],
                    }
                ]

            v2_conds.append({"operands": operands, "operator": "OR"})
            continue

        # 1) wrapper ── ("AND"/"OR", inner)
        if (
            isinstance(cond, (tuple, list))
            and len(cond) == 2
            and str(cond[0]).upper() in ("AND", "OR")
        ):
            op = str(cond[0]).upper()
            inner = cond[1]

            # inner triple
            if isinstance(inner, (tuple, list)) and len(inner) == 3:
                obj, lhs, rhs = inner
                obj = obj.upper()
                if obj in ENTRY_TYPES:
                    operands = [
                        {
                            "object_type": obj,
                            "entry_values": [{"lhs": lhs, "rhs": rhs}],
                        }
                    ]
                else:
                    operands = [
                        {
                            "object_type": obj,
                            "values": [str(rhs)],
                        }
                    ]

            # inner pair
            elif isinstance(inner, (tuple, list)) and len(inner) == 2:
                obj, vals = inner
                obj = obj.upper()
                if (
                    isinstance(vals, list)
                    and vals
                    and all(isinstance(v, (tuple, list)) and len(v) == 2 for v in vals)
                ):
                    operands = [
                        {
                            "object_type": obj,
                            "entry_values": [{"lhs": v[0], "rhs": v[1]} for v in vals],
                        }
                    ]
                else:
                    vals = vals if isinstance(vals, list) else [vals]
                    operands = [{"object_type": obj, "values": [str(v) for v in vals]}]
            else:
                continue

            v2_conds.append({"operands": operands, "operator": op})
            continue

        # 2) plain pair ── (obj, vals / [ (lhs,rhs)... ])
        if isinstance(cond, (tuple, list)) and len(cond) == 2:
            obj, vals = cond
            obj = obj.upper()

            if (
                isinstance(vals, list)
                and vals
                and all(isinstance(v, (tuple, list)) and len(v) == 2 for v in vals)
            ):
                operands = [
                    {
                        "object_type": obj,
                        "entry_values": [{"lhs": v[0], "rhs": v[1]} for v in vals],
                    }
                ]
            else:
                vals = vals if isinstance(vals, list) else [vals]
                operands = [{"object_type": obj, "values": [str(v) for v in vals]}]

            v2_conds.append({"operands": operands})
            continue

        # 3) already a dict
        if isinstance(cond, dict) and "operands" in cond:
            op = str(cond.get("operator", "AND")).upper()
            ops = cond["operands"]
            v2_conds.append({"operands": ops, **({"operator": op} if op else {})})

    # ------------------------------------------------ canonicalise operator for VALUE_TYPES
    for c in v2_conds:
        first_obj = c["operands"][0]["object_type"].upper()
        if first_obj in VALUE_TYPES:
            c["operator"] = "OR"  # API always returns OR for value lists

    # ------------------------------------------------ order-insensitive 'values' lists
    for c in v2_conds:
        for operand in c["operands"]:
            if "values" in operand:
                operand["values"] = sorted(str(v) for v in operand["values"])

    # ------------------------------------------------ stable ordering
    def _key(c):
        obj = c["operands"][0]["object_type"]
        op = c["operator"]
        return (obj, op)

    normalized["conditions"] = sorted(v2_conds, key=_key)

    # ------------------------------------------------ normalize privileged_capabilities
    if "privileged_capabilities" in normalized:
        cap_block = normalized["privileged_capabilities"]

        # If it came from SDK/response (dict with capabilities key)
        if isinstance(cap_block, dict) and "capabilities" in cap_block:
            cap_list = cap_block.get("capabilities", [])
            normalized["privileged_capabilities"] = {
                "clipboard_copy": "CLIPBOARD_COPY" in cap_list,
                "clipboard_paste": "CLIPBOARD_PASTE" in cap_list,
                "file_download": "FILE_DOWNLOAD" in cap_list,
                "file_upload": "FILE_UPLOAD" in cap_list,
                "inspect_file_upload": "INSPECT_FILE_UPLOAD" in cap_list,
                "inspect_file_download": "INSPECT_FILE_DOWNLOAD" in cap_list,
                "monitor_session": "MONITOR_SESSION" in cap_list,
                "record_session": "RECORD_SESSION" in cap_list,
                "share_session": "SHARE_SESSION" in cap_list,
            }

        # If it's already a flag dict (Ansible input), clean falsy/null
        elif isinstance(cap_block, dict):
            normalized["privileged_capabilities"] = {
                k: True for k, v in cap_block.items() if v is True
            }

    return normalized


def map_conditions_v2(conditions_obj):
    """
    Convert Ansible-style condition dicts into the SDK tuple/list syntax.
    """
    if not isinstance(conditions_obj, list):
        return []

    out = []

    for cond in conditions_obj:
        op = (cond.get("operator") or "").upper() or None

        for operand in cond.get("operands", []):
            obj = (
                operand.get("object_type") or operand.get("objectType") or ""
            ).lower()
            if not obj:
                continue

            # ------------------------------------------------ entry_values path
            entry_vals = operand.get("entry_values") or operand.get("entryValues")
            if entry_vals:  # <- guards against None
                pairs = entry_vals if isinstance(entry_vals, list) else [entry_vals]
                tuples = [(str(p["lhs"]), str(p["rhs"])) for p in pairs]

                payload = (
                    (obj, tuples[0][0], tuples[0][1])
                    if len(tuples) == 1
                    else (obj, tuples)
                )
                out.append((op, payload) if op else payload)
                continue

            # ------------------------------------------------ lhs/rhs shorthand
            if "lhs" in operand and "rhs" in operand:
                payload = (obj, str(operand["lhs"]), str(operand["rhs"]))
                out.append((op, payload) if op else payload)
                continue

            # ------------------------------------------------ simple values list
            vals = operand.get("values")
            if vals is None:
                continue
            vals = [vals] if not isinstance(vals, list) else vals
            payload = (obj, [str(v) for v in vals])
            out.append((op, payload) if op else payload)

    # strip (None, payload) wrappers (shouldn't occur, but keeps list clean)
    return [
        p if not (isinstance(p, tuple) and p[0] in [None, ""]) else p[1] for p in out
    ]


def convert_conditions_v1_to_v2(v1_conditions, module=None):
    """
    Convert the API’s v1-style response into the deterministic v2 shape
    Ansible stores – while *preserving* the operator (AND / OR) that came
    from the server.
    """
    import json
    from collections import defaultdict

    if not v1_conditions:
        return []

    VALUE_TYPES = {
        "APP",
        "APP_GROUP",
        "CLIENT_TYPE",
        "MACHINE_GRP",
        "EDGE_CONNECTOR_GROUP",
        "CONSOLE",
        "LOCATION",
        "BRANCH_CONNECTOR_GROUP",
        "CHROME_POSTURE_PROFILE",
    }

    ENTRY_TYPES = {
        "PLATFORM",
        "POSTURE",
        "TRUSTED_NETWORK",
        "SAML",
        "SCIM",
        "SCIM_GROUP",
        "COUNTRY_CODE",
        "RISK_FACTOR_TYPE",
        "CHROME_ENTERPRISE",
    }

    module and module.warn(
        f"[convert_conditions_v1_to_v2] Input (v1-style): {json.dumps(v1_conditions, indent=2)}"
    )

    # (operator, object_type) → list(ids)   …for value-based object types
    grouped_values: dict[tuple[str, str], list[str]] = defaultdict(list)
    v2_conditions = []

    for condition in v1_conditions:
        cond_op = (condition.get("operator") or "OR").upper()

        for operand in condition.get("operands", []):
            obj = (
                operand.get("objectType") or operand.get("object_type") or ""
            ).upper()
            if not obj:
                continue

            # ----------------------------- VALUE-BASED object types
            if obj in VALUE_TYPES:
                rhs_id = str(operand.get("rhs"))
                grouped_values[(cond_op, obj)].append(rhs_id)

            # ----------------------------- ENTRY-VALUE object types
            elif obj in ENTRY_TYPES:
                lhs = str(operand.get("lhs"))
                rhs = str(operand.get("rhs"))
                v2_conditions.append(
                    {
                        "operands": [
                            {
                                "object_type": obj,
                                "entry_values": [{"lhs": lhs, "rhs": rhs}],
                            }
                        ],
                        "operator": cond_op,
                    }
                )

    # build one condition per (operator, object_type) for value-based items
    for (op, obj), ids in grouped_values.items():
        v2_conditions.append(
            {
                "operands": [
                    {
                        "object_type": obj,
                        "values": sorted(ids),
                    }
                ],
                "operator": op,
            }
        )

    # stable order → avoids diff shuffle
    v2_conditions.sort(key=lambda c: (c["operands"][0]["object_type"], c["operator"]))

    module and module.warn(
        f"[convert_conditions_v1_to_v2] Output (v2-style): {json.dumps(v2_conditions, indent=2)}"
    )
    return v2_conditions


def validate_operand_v2(operand, module):
    object_type = str(operand.get("object_type", "")).upper()
    if not object_type:
        return "object_type is required in each operand."

    VALUE_OBJECT_TYPES = {
        "APP",
        "APP_GROUP",
        "CONSOLE",
        "MACHINE_GRP",
        "EDGE_CONNECTOR_GROUP",
        "LOCATION",
        "CLIENT_TYPE",
        "CHROME_POSTURE_PROFILE",
    }

    ENTRY_OBJECT_TYPES = {
        "PLATFORM",
        "COUNTRY_CODE",
        "SCIM_GROUP",
        "SCIM",
        "SAML",
        "RISK_FACTOR_TYPE",
        "CHROME_ENTERPRISE",
        "POSTURE",
        "TRUSTED_NETWORK",
    }

    if object_type not in VALUE_OBJECT_TYPES | ENTRY_OBJECT_TYPES:
        return (
            f"Invalid object_type: {object_type}. Supported types: "
            f"{', '.join(sorted(VALUE_OBJECT_TYPES | ENTRY_OBJECT_TYPES))}"
        )

    # ---------------------------------------------------------------- values-style
    if object_type in VALUE_OBJECT_TYPES:
        values = operand.get("values")
        if not isinstance(values, list) or not values:
            return f"'values' must be a non-empty list for {object_type}"

        if object_type == "CLIENT_TYPE":
            allowed = [
                "zpn_client_type_exporter",
                "zpn_client_type_machine_tunnel",
                "zpn_client_type_edge_connector",
                "zpn_client_type_vdi",
                "zpn_client_type_zapp",
                "zpn_client_type_browser_isolation",
                "zpn_client_type_ip_anchoring",
                "zpn_client_type_zapp_partner",
                "zpn_client_type_branch_connector",
            ]
            bad = [v for v in values if v not in allowed]
            if bad:
                return (
                    f"Invalid CLIENT_TYPE value(s): {', '.join(bad)}. "
                    f"Permitted values: {', '.join(allowed)}"
                )

        if object_type == "CHROME_POSTURE_PROFILE":
            if not all(isinstance(v, str) and v.strip() for v in values):
                return "For CHROME_POSTURE_PROFILE, all values must be non-empty profile ID strings."

        return None  # ✅ nothing more to check for other value-types

    # ----------------------------------------------------------- entry_values-style
    ev = operand.get("entry_values")
    if not isinstance(ev, dict):
        return f"'entry_values' must be a dict for {object_type}"
    if not ev.get("lhs") or not ev.get("rhs"):
        return "'entry_values' must contain non-empty 'lhs' and 'rhs'"

    if object_type == "PLATFORM":
        allowed = ["android", "ios", "linux", "mac", "windows"]
        lhs = str(ev["lhs"]).lower()
        rhs = str(ev["rhs"]).lower()
        if lhs not in allowed:
            return f"Invalid PLATFORM lhs: {lhs}. Permitted: {', '.join(allowed)}"
        if rhs != "true":
            return "For PLATFORM, rhs must be 'true'."

    if object_type == "COUNTRY_CODE":
        lhs = str(ev["lhs"]).upper()
        rhs = str(ev["rhs"]).lower()
        if not validate_iso3166_alpha2(lhs):
            return f"Invalid COUNTRY_CODE lhs: '{lhs}' is not a valid ISO3166 Alpha2 country code. Please visit the following site for reference: https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes"
        if rhs != "true":
            return "For COUNTRY_CODE, rhs must be 'true'."

    if object_type == "RISK_FACTOR_TYPE":
        lhs = str(ev["lhs"])
        rhs = str(ev["rhs"]).upper()
        allowed = {"UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
        if lhs != "ZIA":
            return "For RISK_FACTOR_TYPE, lhs must be 'ZIA'."
        if rhs not in allowed:
            return f"Invalid RISK_FACTOR_TYPE rhs: {rhs}. Permitted values: {', '.join(sorted(allowed))}"

    if object_type == "CHROME_ENTERPRISE":
        lhs = str(ev["lhs"])
        rhs = str(ev["rhs"]).lower()
        if lhs != "managed":
            return "For CHROME_ENTERPRISE, lhs must be 'managed'."
        if rhs not in {"true", "false"}:
            return "For CHROME_ENTERPRISE, rhs must be either 'true' or 'false'."

    return None  # ✓ valid


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
