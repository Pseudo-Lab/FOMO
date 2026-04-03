"""
JSON Schema 검증기
역할: HTTP 응답 body가 expected_schema에 맞는지 검사

jsonschema 라이브러리 사용 (없으면 기본 타입 검사로 폴백).
"""


def validate_schema(data, schema: dict) -> bool:
    """
    data가 JSON Schema를 만족하면 True, 아니면 False.
    ※ schema가 None이면 검증 생략 → True 반환.
    """
    if schema is None:
        return True

    try:
        import jsonschema
        jsonschema.validate(instance=data, schema=schema)
        return True
    except ImportError:
        # jsonschema 없을 때 기본 검사로 폴백
        return _basic_validate(data, schema)
    except jsonschema.ValidationError:
        return False


def _basic_validate(data, schema: dict) -> bool:
    """jsonschema 미설치 환경용 최소 타입 검사."""
    _type_map = {
        "object": dict,
        "array": list,
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "null": type(None),
    }

    expected_type = schema.get("type")
    if expected_type:
        expected_cls = _type_map.get(expected_type, object)
        if not isinstance(data, expected_cls):
            return False

    # object: required 필드 존재 여부
    if expected_type == "object" and isinstance(data, dict):
        for key in schema.get("required", []):
            if key not in data:
                return False

    # array: items 스키마 재귀 검사
    if expected_type == "array" and isinstance(data, list):
        item_schema = schema.get("items")
        if item_schema:
            return all(_basic_validate(item, item_schema) for item in data)

    return True
