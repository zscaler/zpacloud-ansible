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

# We are implementing custom validation that will be shared across all policy types

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
    lhs = operand.get("lhs", "").strip()
    rhs = operand.get("rhs", "").strip()

    client = ZPAClientHelper(module)

    if object_type == "POSTURE":
        try:
            profile = client.posture_profiles.get_profile_by_postureUdid(posture_udid=lhs)
            print(profile) # Debugging line
            if not profile:
                return lhsWarn(object_type, "valid posture profile ID", lhs)
            if not profile:
                return lhsWarn(object_type, "valid posture profile ID", lhs)

            if rhs not in ["true", "false"]:
                return rhsWarn(object_type, "\"true\"/\"false\"", rhs)

        except Exception as e:
            return "Error retrieving Posture Profile with ID '%s': %s" % (lhs, str(e))

    # ... other cases ...

    return None
