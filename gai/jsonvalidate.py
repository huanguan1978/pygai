#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json

# from collections import namedtuple
from typing import NamedTuple, Union, Optional
from jsonschema import validate as jsonScheamValidate
from jsonschema import ValidationError, SchemaError, ErrorTree


JsonValidateResult = NamedTuple('JsonValidateResult',
                                [('ok', bool), ('message', str)]
                                )
def jsonValidate(jsonData:object, jsonSchema:Optional[dict], isDecoded:bool = True)->JsonValidateResult:

    data = None
    if not isDecoded and isinstance(jsonData, str):
        try:
            data = json.loads(jsonData) # type: ignore
        except ValueError as err:
            print('ValueError'); print(str(err))                
            return JsonValidateResult(ok=False, message=str(err))
    
    if data and jsonSchema:
        try:
            jsonScheamValidate(instance=data, schema=jsonSchema)
        except SchemaError as err:
            print('SchemaError'); print(str(err))                
            return JsonValidateResult(ok=False, message=str(err))
        except ValidationError as err:
            print('ValidationError'); print(str(err))                
            return JsonValidateResult(ok=False, message=str(err))
        else:
            pass

    return JsonValidateResult(ok=True, message='')


jsendSchemaQuacking = {
    "type": "object",
    "required": ["status", "data"],
    "properties": {
        "status": {
            "type": "string",
            "enum": ["success", "fail", "error"],
        },
        "data": {
            "type": "object",
            "required": ["id", "text", "type"],
            "properties": {
                "id": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                "text": {"type": "string"},
                "type": {
                    "type": "string", 
                    "enum": ["gentxt", "genimg"],
                },
                "cronId": {"type": "string"},
                "histId": {"type": "string"},                
                "promptId": {"type": "string"},
                "files": {
                    "anyOf": [
                        {"type": "array", "items": {"type": "string"}},
                        {"type": "string"},              
                    ]
                },
            }
        }
    }
}

