from typing import Any, Dict, Optional
import json
import re

OPERATORS = {
    ">": "$gt",
    "<": "$lt",
    ">=": "$gte",
    "<=": "$lte",
    "=": "$eq",
    "!=": "$ne",
    "between": "$gte_lte",
}


def parse_operator_filter(field: str, raw: Optional[str]) -> Dict[str, Any]:
    if not raw:
        return {}

    try:
        parsed = json.loads(raw)
        op = parsed[0]
        value = parsed[1]

        if op not in OPERATORS:
            raise ValueError(f"Unsupported operator: {op}")

        mongo_op = OPERATORS[op]

        if mongo_op == "$gte_lte":
            return {field: {"$gte": value[0], "$lte": value[1]}}
        else:
            return {field: {mongo_op: value}}

    except Exception as e:
        raise ValueError(f"Invalid filter format for {field}: {str(e)}")


TEXT_OPERATORS = {
    "contains": "$regex_contains",
    "startswith": "$regex_startswith",
    "endswith": "$regex_endswith",
    "=": "$eq",
    "!=": "$ne",
    "in": "$in",
}


def parse_text_filter(field: str, raw: Optional[str]) -> Dict[str, Any]:
    if not raw:
        return {}

    try:
        parsed = json.loads(raw)
        op = parsed[0]
        value = parsed[1]

        if op not in TEXT_OPERATORS:
            raise ValueError(f"Unsupported text operator: {op}")

        mongo_op = TEXT_OPERATORS[op]

        if mongo_op == "$regex_contains":
            return {
                field: {"$regex": re.escape(value), "$options": "i"}
            }  # case-insensitive
        elif mongo_op == "$regex_startswith":
            return {field: {"$regex": f"^{re.escape(value)}", "$options": "i"}}
        elif mongo_op == "$regex_endswith":
            return {field: {"$regex": f"{re.escape(value)}$", "$options": "i"}}
        elif mongo_op == "$in":
            if not isinstance(value, list):
                raise ValueError("Value for 'in' must be a list")
            return {field: {"$in": value}}
        else:
            return {field: {mongo_op: value}}

    except Exception as e:
        raise ValueError(f"Invalid text filter format for {field}: {str(e)}")
