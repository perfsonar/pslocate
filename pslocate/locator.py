from elasticsearch import Elasticsearch
import re

#OUTPUT settings
DEBUG = False

#constants for LS records
##source address
FIELD_SRC = 'psmetadata-src-address'
##destination address
FIELD_DST = 'psmetadata-dst-address'
##address list
FIELD_INDEX_ADDRS = 'psmetadata-index-packet-trace-addresses'
##distance from source
FIELD_INDEX_SRCD = 'psmetadata-index-packet-trace-srchops'
## distance from dest
FIELD_INDEX_DSTD = 'psmetadata-index-packet-trace-dsthops'
##list of required fields
REQUIRED_FIELDS = [FIELD_SRC, FIELD_DST, FIELD_INDEX_ADDRS, FIELD_INDEX_SRCD, FIELD_INDEX_DSTD]

def pslocate(elastic_servers, input_hops):
    # Search elastic
    ##TODO: Paginate
    client = Elasticsearch(elastic_servers)
    response = client.search(
        index="perfsonar",
        size="10000",
        body={
            "query": {
                "constant_score": {
                    "filter": {
                        "terms": {
                            FIELD_INDEX_ADDRS: input_hops
                        },
                    }
                }
            }
        }
    )

    #iterate results and find closest endpoints
    scores = {}
    for hit_raw in response['hits']['hits']:
        hit = hit_raw['_source']
    
        #validate record and silently skip malformed ones
        valid = True
        for req_field in REQUIRED_FIELDS:
            if req_field not in hit or not hit[req_field]:
                valid = False
                break
        if not valid:
            continue
    
        #go through each hop in the traceroute index for this record
        src = hit[FIELD_SRC][0]
        dst = hit[FIELD_DST][0]
        if DEBUG:
            print "Source: %s  Destination: %s" % (hit[FIELD_SRC][0], hit[FIELD_DST][0])
            print "%s" % hit[FIELD_INDEX_ADDRS]
        for hop_index, hop_addr in enumerate(hit[FIELD_INDEX_ADDRS]):
            #don't care about hops not in the list
            if hop_addr not in input_hops:
                continue
            
            #get distance from source
            if hop_addr == src:
                src_distance = 0
            elif len(hit[FIELD_INDEX_SRCD]) > hop_index:
                src_distance = hit[FIELD_INDEX_SRCD][hop_index]
            else:
                #malformed or old record that doesn't have required distance count
                continue
            
            #get distance from dest
            if hop_addr == dst:
                dst_distance = 0
            elif len(hit[FIELD_INDEX_DSTD]) > hop_index:
                dst_distance = hit[FIELD_INDEX_DSTD][hop_index]
            else:
                #malformed or old record that doesn't have required distance count
                continue
        
            #init scores
            if hop_addr not in scores:
                scores[hop_addr] = {}
        
            #take the best case distance (worst case seems to give less accurate results?)
            if src not in scores[hop_addr] or scores[hop_addr][src] > src_distance:
                scores[hop_addr][src] = src_distance
            if dst not in scores[hop_addr] or scores[hop_addr][dst] > dst_distance:
                scores[hop_addr][dst] = dst_distance

    #sort results for each hop with closest nodes first
    sorted_scores = {}
    for score_hop in scores:
        tmp_sorted = sorted(scores[score_hop].items(), key=lambda x: int(x[1]))
        sorted_scores[score_hop] = map(lambda x: {'address': x[0], 'score': x[1] }, tmp_sorted)
    
    return sorted_scores

def parse_traceroute(traceroute_output):
    ips = []
    for line in traceroute_output.splitlines():
        if line.startswith('traceroute'):
            #skip first line of traceroute
            continue
        stripped_line = line.rstrip().lstrip()
        ipv4_match = re.search('\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b', stripped_line)
        if ipv4_match:
            ips.append(ipv4_match.group(0))
            continue
        ipv6_match = re.search('\\A(?:(?:(?:[A-Fa-f0-9]{1,4}:){6}|(?=(?:[A-Fa-f0-9]{0,4}:){0,6}(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\Z)(([0-9A-Fa-f]{1,4}:){0,5}|:)((:[0-9A-Fa-f]{1,4}){1,5}:|:)|::(?:[A-Fa-f0-9]{1,4}:){5})(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])|(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}|(?=(?:[A-Fa-f0-9]{0,4}:){0,7}[A-Fa-f0-9]{0,4}\\Z)(([0-9A-Fa-f]{1,4}:){1,7}|:)((:[0-9A-Fa-f]{1,4}){1,7}|:)|(?:[A-Fa-f0-9]{1,4}:){7}:|:(:[A-Fa-f0-9]{1,4}){7})\\Z', stripped_line)
        if ipv6_match:
            ips.append(ipv6_match.group(0))
    return ips
        
    