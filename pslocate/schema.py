import os
import sys
import json

pslocate_search_request_schema = {
    "$schema": "http://json-schema.org/schema#",
    "id": "http://perfsonar.net/schema/pslocate-search",
    "title": "pSLocate Search Request Schema",
    "type": "object",
    "oneOf": [
        {
            "properties": {
                "filter-type": {
                    "description": "Indicates a list of IPs will be provided as the filter",
                    "type": "string",
                    "enum": [ "ips" ] 
                },
                "filter": {
                    "description": "The list of ips for which to find the closest measurement points",
                    "type": "array",
                    "items": {
                        "type": "string",
                        "format": "hostname"
                    }
                }   
            }
        },
        {
            "properties": {
                "filter-type": {
                    "description": "Indicates that the IP list should be extracted from the provided raw traceroute output",
                    "type": "string",
                    "enum": [ "traceroute" ] 
                },
                "filter": {
                    "description": "The raw output of the traceroute command",
                    "type": "string"
                }      
            }
        }
    ],
    "required": ["filter-type", "filter"]
}


'''
Load a JSON schema file from the current working directory
'''
def _load_schema(schema_file):
    #find schema file
    schema_path = os.path.dirname(sys.argv[0])  
    if schema_path and not schema_path.endswith(os.sep):
        schema_path += os.sep
    try:
        schema = json.loads(open(schema_path + schema_file).read())
    except Exception, e:
        abort(500, "Problem loading schema file: %s" % e)
    
    return schema