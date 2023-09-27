from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pycountry
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

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
                    'objectType': op.get('object_type'),
                    'lhs': op.get('lhs'),
                    'rhs': op.get('rhs'),
                    'id': op.get('id'),
                    'idp_id': op.get('idp_id'),
                    'name': op.get('name'),
                }
                # Filter out None values
                mapped_operand = {k: v for k, v in mapped_operand.items() if v is not None}
                mapped_operands.append(mapped_operand)

            mapped_condition = {
                'id': condition.get('id'),
                'negated': condition.get('negated'),
                'operator': condition.get('operator'),
                'operands': mapped_operands
            }
            # Filter out None values
            mapped_condition = {k: v for k, v in mapped_condition.items() if v is not None}
            result.append(mapped_condition)

    return result

def normalize_policy(policy):
    normalized = policy.copy()

    # Exclude the computed values from the data
    computed_values = ["modified_time", "creation_time", "modified_by", "rule_order"]
    for attr in computed_values:
        normalized.pop(attr, None)

    # Normalize action attribute
    if "action" in normalized:
        normalized["action"] = normalized["action"].upper()

    # Remove IDs from conditions and operands but keep the main policy rule ID
    for condition in normalized.get('conditions', []):
        condition.pop('id', None)  # remove ID from condition
        for operand in condition.get('operands', []):
            operand.pop('id', None)  # remove ID from operand
            operand.pop('name', None)  # remove name from operand

            # Adjust the operand key from "objectType" to "object_type"
            if 'objectType' in operand:
                operand['object_type'] = operand.pop('objectType')

    return normalized


def validate_operand(operand, module):
    def lhsWarn(object_type, expected, got, error=None):
        error_msg = f"Invalid LHS for '{object_type}'. Expected {expected}, but got '{got}'"
        if error:
            error_msg += f". Error details: {error}"
        return error_msg

    def rhsWarn(object_type, expected, got, error=None):
        error_msg = f"Invalid RHS for '{object_type}'. Expected {expected}, but got '{got}'"
        if error:
            error_msg += f". Error details: {error}"
        return error_msg

    object_type = operand.get("objectType", "").upper()
    lhs = operand.get("lhs")
    rhs = operand.get("rhs")

    # Check lhs and rhs for emptiness
    if lhs is None or not lhs.strip():
        return lhsWarn(object_type, "a non-empty value", "empty or None")
    if rhs is None or not rhs.strip():
        return rhsWarn(object_type, "a non-empty value", "empty or None")

    lhs = lhs.strip()
    rhs = rhs.strip()

    client = ZPAClientHelper(module)

    object_validations = {
        "APP": {
            "lhs": ["id"],
            "fetch_method": client.app_segments.get_segment,
            "kwargs": {"id": rhs},
            "rhs_msg": "valid application segment ID",
        },
        "APP_GROUP": {
            "lhs": ["id"],
            "fetch_method": client.segment_groups.get_group,
            "kwargs": {"id": rhs},
            "rhs_msg": "valid segment group ID",
        },
        "MACHINE_GRP": {
            "lhs": ["id"],
            "fetch_method": client.machine_groups.get_group,
            "kwargs": {"id": rhs},
            "rhs_msg": "valid machine group ID",
        },
        "EDGE_CONNECTOR_GROUP": {
            "lhs": ["id"],
            "fetch_method": client.cloud_connector_groups.get_group,
            "kwargs": {"id": rhs},
            "rhs_msg": "valid cloud connector ID",
        },
        "POSTURE": {
            "rhs": ["true", "false"],
            "fetch_method": client.posture_profiles.get_profile_by_posture_udid,
            "kwargs": {"posture_udid": lhs},
            "lhs_msg": "valid posture profile ID",
        },
        "TRUSTED_NETWORK": {
            "rhs": ["true", "false"],
            "fetch_method": client.trusted_networks.get_by_network_id,
            "kwargs": {"network_id": lhs},
            "lhs_msg": "valid trusted network ID",
        },
        "PLATFORM": {
            "rhs": ["true"],
            "lhs": ['linux', 'android', 'windows', 'ios', 'mac'],
            "lhs_msg": "one of ['linux', 'android', 'windows', 'ios', 'mac']",
        },
        "COUNTRY_CODE": {
            "rhs": ["true"],
            "lhs": validate_iso3166_alpha2,  # Using the function directly here
            "lhs_msg": "valid ISO-3166 Alpha-2 country code. Please visit the following site for reference: https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes",
        },
        "CLIENT_TYPE": {
            "lhs": ["id"],
            "lhs_msg": "the string 'id'",
            "rhs": [
                'zpn_client_type_exporter',
                'zpn_client_type_exporter_noauth',
                'zpn_client_type_browser_isolation',
                'zpn_client_type_machine_tunnel',
                'zpn_client_type_ip_anchoring',
                'zpn_client_type_edge_connector',
                'zpn_client_type_zapp',
                'zpn_client_type_slogger',
                'zpn_client_type_zapp_partner',
                'zpn_client_type_branch_connector'
            ],
            "rhs_msg": "one of ['zpn_client_type_exporter', zpn_client_type_exporter_noauth, zpn_client_type_browser_isolation, zpn_client_type_machine_tunnel, zpn_client_type_ip_anchoring, zpn_client_type_edge_connector, zpn_client_type_zapp, zpn_client_type_s]"
        },
    }

    validation = object_validations.get(object_type)

    if validation:
        # Validate LHS
        if "lhs" in validation and lhs not in validation["lhs"]:
            return lhsWarn(object_type, validation["lhs_msg"], lhs)

        # Validate RHS for APP, APP_GROUP, MACHINE_GRP, and EDGE_CONNECTOR_GROUP
        if object_type in ["APP", "APP_GROUP", "MACHINE_GRP", "EDGE_CONNECTOR_GROUP"]:
            try:
                result = validation["fetch_method"](**validation["kwargs"])
                if not result or result.get('id') != rhs:
                    return rhsWarn(object_type, validation["rhs_msg"], rhs)
            except Exception as e:
                fetch_msg = f"Error retrieving {object_type} with ID '{rhs}': {str(e)}"
                return fetch_msg

        # Validate RHS for other types (POSTURE, TRUSTED_NETWORK, PLATFORM, CLIENT_TYPE)
        elif rhs not in validation["rhs"]:
            return rhsWarn(object_type, validation["rhs_msg"], rhs)

        # Validate LHS for POSTURE and TRUSTED_NETWORK
        if object_type in ["POSTURE", "TRUSTED_NETWORK"]:
            try:
                result = validation["fetch_method"](**validation["kwargs"])
                if not result:
                    return lhsWarn(object_type, validation["lhs_msg"], lhs)
            except Exception as e:
                fetch_msg = f"Error retrieving {object_type} with ID '{lhs}': {str(e)}"
                return fetch_msg

        # Specific LHS Validation for PLATFORM and COUNTRY_CODE
        if object_type == "PLATFORM" and lhs not in ['linux', 'android', 'windows', 'ios', 'mac']:
            return lhsWarn(object_type, "one of ['linux', 'android', 'windows', 'ios', 'mac']", lhs)
        if object_type == "COUNTRY_CODE" and not validate_iso3166_alpha2(lhs):
            return lhsWarn(object_type, "a valid ISO-3166 Alpha-2 country code", lhs)

    return None

def validate_iso3166_alpha2(country_code):
    """
    Validates if the provided country code is a valid 2-letter ISO3166 Alpha2 code.

    :param country_code: 2-letter country code
    :return: True if valid, False otherwise
    """
    try:
        country = pycountry.countries.get(alpha_2=country_code)
        return country is not None
    except AttributeError:
        return False