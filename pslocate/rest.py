import jsonschema 
from locator import pslocate, parse_traceroute
from schema import pslocate_search_request_schema
from flask import Flask, jsonify, request, abort

app = Flask(__name__)
app.config.from_envvar('PSLOCATE_SETTINGS')
ELASTIC_SERVERS = app.config.get("ELASTIC_SERVERS", ["perfsonar-dev.es.net"])
KEY_FILTER_TYPE = "filter-type"
KEY_FILTER_VALUE = "filter"

@app.route('/search', methods=['GET'])
def search_by_ips(): 
    sorted_scores = pslocate(ELASTIC_SERVERS, request.args.getlist('ip'))
    return jsonify(sorted_scores)

@app.route('/search', methods=['POST'])
def search_filter(): 
    #get body
    content = request.get_json(force=True)
    #validate
    try:
        jsonschema.validate(content, pslocate_search_request_schema, format_checker=jsonschema.FormatChecker())
    except Exception, e:
        abort(500, e.message)
    #query
    if content[KEY_FILTER_TYPE] == "ips":
        sorted_scores = pslocate(ELASTIC_SERVERS, content[KEY_FILTER_VALUE])
    elif content[KEY_FILTER_TYPE] == "traceroute":
        ip_list = parse_traceroute(content[KEY_FILTER_VALUE])
        print ip_list
        sorted_scores = pslocate(ELASTIC_SERVERS, ip_list)
    else:
        abort(500, "Filter type not yet supported")
    #return result
    return jsonify(sorted_scores)

@app.errorhandler(500)
def page_not_found(error):
    return jsonify(message=error.description)

if __name__ == '__main__':
    app.run(debug=True)
