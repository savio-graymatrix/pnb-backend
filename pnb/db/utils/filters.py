from typing import Any, Dict, Optional
import json

OPERATORS = {
    ">": "$gt",
    "<": "$lt",
    ">=": "$gte",
    "<=": "$lte",
    "=": "$eq",
    "!=": "$ne",
    "between": "$gte_lte"
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
            return {
                field: {
                    "$gte": value[0],
                    "$lte": value[1]
                }
            }
        else:
            return {
                field: {
                    mongo_op: value
                }
            }

    except Exception as e:
        raise ValueError(f"Invalid filter format for {field}: {str(e)}")