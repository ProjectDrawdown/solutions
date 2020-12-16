import json
from jsonschema import validate

workbook_schema = {
    "type" : "object",
    "properties" : {
        "name" : {"type" : "string"},
        "author" : {"type" : "string"},
        "ui" : {
            "type" : "object",
            "properties": {
                "portfolioSolutions": {"type" : "array"},
                "openPanel" : {"type" : "string"},
                "quickVariables": {"type": "array"},
            }},
        "projectionSettings": {
            "type": "object",
            "properties": {
                "startYear": {"type" : "number"},
                "endYear": {"type" : "number"}
            }
        },
        "projections": {
            "type": "array"
        }
    },
}
