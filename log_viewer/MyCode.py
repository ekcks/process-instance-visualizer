from .XESRead import LogReading
import networkx
import json
import sys
 
def read_from_path(path):
    xeslog = LogReading(path)
    log = []
    for elem in xeslog:
        trace = []
        for event in elem:
            trace.append(event.split('!!'))
        log.append(trace)
    length = len(log)
    return log, length

def make_cyto_json(log, index):
    G = networkx.DiGraph() 
    trace = log[index]
    #for i in trace:
     #   print(i)
    for event in trace:
        G.add_node(event[0], event_name=event[0], performer_name=event[1],  time_stamp=event[2])
    for i in range(len(trace)-1):
        if G.has_edge(trace[i][0], trace[i+1][0]):
            G[trace[i][0]][trace[i+1][0]]['weight'] += 1
        else:
            G.add_edge(trace[i][0], trace[i+1][0], weight=1)
    json = networkx.cytoscape_data(G)
    return json

def get_cytoscape():
    mylog, myindex = read_from_path(sys.argv[1])
    if (not sys.argv[2].isdigit()) or int(sys.argv[2]) < 0 or int(sys.argv[2]) >= myindex:
         print(None)
    else:
        my_json = make_cyto_json(mylog, int(sys.argv[2]))
        json_val = json.dumps(my_json)
        with open("xes_log.json", "w") as json_file:
            json.dump(json_val, json_file)


def make_cyto_json_by_trace(trace):
    G = networkx.DiGraph() 
    for event in trace:
        G.add_node(event[0], event_name=event[0], performer_name=event[1],  time_stamp=event[2])
    for i in range(len(trace)-1):
        if G.has_edge(trace[i][0], trace[i+1][0]):
            G[trace[i][0]][trace[i+1][0]]['weight'] += 1
        else:
            G.add_edge(trace[i][0], trace[i+1][0], weight=1)
    json = networkx.cytoscape_data(G)
    return json

if __name__ == "__main__":
    log, length = read_from_path('C:/Users/jdc/Documents/카카오톡 받은 파일/review_example_large.xes')
    print(log)
    #get_cytoscape()