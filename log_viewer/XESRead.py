import xml.etree.ElementTree as ET

# for event, elem in ET.iterparse('2.xes', events=("start", "end")):
#     if event == "start":
#         print('element tag:', elem.tag)
#         print('elemnt attrib list:', elem.attrib)
#         if 'name' in elem.attrib:
#             print('element attrib name:', elem.attrib['name'])
#     else:
#         print('element tag:', elem.tag)
#         print('element text:', elem.text)
import pandas as pd
from numpy.core.defchararray import strip

from .Helper.Commons.Variables import *

events = ("start", "end")


def Save_XES_Log_list(_log_list, _file_path):
    try:
        f = open(_file_path, 'w', encoding='utf-8')
        f.write(key_connect_node + '\n')
        f.write(key_connect_inside + '\n')
        for trace in _log_list:
            line = key_connect_node.join([str(elem) for elem in trace])
            print('saved: %s' % line)
            f.write(line + '\n')
    finally:
        f.close()


def LogReading(_input_log=''):
    log_list_string = []
    try:
        startTrace, endTrace, startEvent, endEvent = False, False, False, False
        trace_list, event_list = [], []
        if '.xes' in _input_log:
            for event, elem in ET.iterparse(_input_log, events=events):
                this_tag = elem.tag.replace(r'{http://www.xes-standard.org/}', '')
                if event == "start":
                    if 'trace' in this_tag:
                        startTrace, endTrace, startEvent, endEvent = True, False, False, False
                        event_list = ['START' + key_connect_inside + 'START' + key_connect_inside + 'START']
                    elif 'event' in this_tag:
                        startEvent = True
                        this_act, this_per, this_time = "NULL", "NULL", "NULL"

                    if 'key' in elem.attrib:
                        if startEvent:
                            this_val = elem.attrib['value']
                            if elem.attrib['key'] == activity_key:
                                this_act = this_val
                            elif elem.attrib['key'] == performer_key:
                                this_per = this_val
                            elif elem.attrib['key'] == timestamp_key:
                                this_time = this_val

                        elif startTrace and (not endTrace) and (elem.attrib['key'] == activity_key):
                            trace_list.append(elem.attrib['value'])
                elif event == "end":
                    if 'event' in this_tag:
                        startEvent = False
                        this_event = this_act + key_connect_inside + this_per + key_connect_inside + this_time
                        event_list.append(this_event)
                    elif 'trace' in this_tag:
                        startTrace = False
                        event_list.append('END' + key_connect_inside + 'END' + key_connect_inside + 'END')
                        log_list_string.append(event_list)
        else:  # input file is TXT.
            log_list_string = LogFileToTraceList(_input_log)
    except Exception as e:
        print(f'---Error: {e}')
    finally:
        return log_list_string



def LogFileToTraceList(_filePath):
    _keyWordSeparate, _keySeparateInside = '', ''
    _traceList = []
    with open(_filePath, encoding='utf-8') as f:
        _keyWordSeparate = f.readline().strip()
        _keySeparateInside = f.readline().strip()
        while True:
            currentLine = f.readline()
            if not currentLine:
                break
            currentTrace = currentLine.strip().split(_keyWordSeparate)
            _traceList.append(currentTrace)
    return _traceList


if __name__ == '__main__':
    file_p = "Logs/0 XES Example.xes"
    xesLog = LogReading(file_p)
    for trace in xesLog:
        print(trace)
