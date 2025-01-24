from .MyCode import read_from_path, make_cyto_json, make_cyto_json_by_trace


def process_xes_log(log_path):
    return read_from_path(log_path)

def process_json(log, index):
    return make_cyto_json(log, index)

def process_json_by_group(trace):
    return make_cyto_json_by_trace(trace)


