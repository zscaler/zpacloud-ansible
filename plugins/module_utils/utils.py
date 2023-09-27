from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pycountry


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

    object_type = operand.get("object_type", "").upper()
    lhs = operand.get("lhs")
    rhs = operand.get("rhs")

    # Validate non-emptiness
    if not object_type or not lhs or not rhs:
        return "Object type, LHS, and RHS cannot be empty or None"

    # Ensure lhs and rhs are strings
    if not isinstance(lhs, str):
        lhs = str(lhs)
    if not isinstance(rhs, str):
        rhs = str(rhs)

    valid_object_types = ["APP", "APP_GROUP", "MACHINE_GRP", "EDGE_CONNECTOR_GROUP", "POSTURE", "TRUSTED_NETWORK", "PLATFORM", "COUNTRY_CODE", "CLIENT_TYPE"]

    if object_type not in valid_object_types:
        return f"Invalid object type: {object_type}. Supported types are: {', '.join(valid_object_types)}"

    if object_type in ["APP", "APP_GROUP", "MACHINE_GRP", "EDGE_CONNECTOR_GROUP"]:
        if lhs != 'id':
            return lhsWarn(object_type, 'id', lhs)
        if not rhs:
            return rhsWarn(object_type, "non-empty string", rhs)

    elif object_type in ["POSTURE", "TRUSTED_NETWORK"]:
        if rhs not in ['true', 'false']:
            return rhsWarn(object_type, "one of ['true', 'false']", rhs)

    elif object_type == "PLATFORM":
        if rhs != 'true':
            return rhsWarn(object_type, 'true', rhs)
        if lhs not in ['linux', 'android', 'windows', 'ios', 'mac']:
            return lhsWarn(object_type, "one of ['linux', 'android', 'windows', 'ios', 'mac']", lhs)

    elif object_type == "COUNTRY_CODE":
        if rhs != 'true':
            return rhsWarn(object_type, 'true', rhs)
        if not validate_iso3166_alpha2(lhs):
            return lhsWarn(object_type, "a valid ISO-3166 Alpha-2 country code", lhs, "Please visit the following site for reference: https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes")

    elif object_type == "CLIENT_TYPE":
        if lhs != 'id':
            return lhsWarn(object_type, 'id', lhs)
        valid_client_types = [
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
        ]
        if rhs not in valid_client_types:
            return rhsWarn(object_type, f"one of {valid_client_types}", rhs)

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