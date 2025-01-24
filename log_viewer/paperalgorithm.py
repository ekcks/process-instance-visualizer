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
from anytree import Node, RenderTree, find
from anytree.exporter import DotExporter
from anytree.search import findall
from Helper.Commons.Variables import *

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




def makeGroupArray(log):
    groupArray = []
    for elem in log:
        if elem not in groupArray:
            #print(elem)
            groupArray.append(elem)
    return groupArray, len(groupArray)


def makePartialArray(array,index):
    return list(map(lambda x: array[x], index))


def makeStringToArray(groupArray):
    return list(map(lambda sublist: list(map(lambda item: item.split('!!')[0], sublist)), groupArray))


def makeGroupFragmentArray(groupArray):
    return list(map(lambda lst: list(zip(lst[:-1], lst[1:])), groupArray))

def makeGroupFragict(groupFragmentArray):
    groupFragDict = {}
    for groupfrag in groupFragmentArray:
        for (src,dest) in groupfrag:
            if src not in groupFragDict.keys():
                groupFragDict[src] = [dest]
            else:
                groupFragDict[src].append(dest)
    groupFragDict['END'] = []
    return groupFragDict




def getParentNode(node, nonDuplicateGroupFragDict):
    parents = []
    for key in nonDuplicateGroupFragDict.keys():
        if node in nonDuplicateGroupFragDict[key]:
            parents.append(key)
    return parents


class TraceLoop:
    def __init__(self):
        self.traces = []
    
    def folding(self, trace):
        """ 간단한 folding 함수: 중복된 연속 활동을 제거 """
        folded_trace = []
        previous_activity = None
        
        for activity in trace:
            if activity != previous_activity:
                folded_trace.append(activity)
            previous_activity = activity
        
        return folded_trace

    '''
    테스트용 함수(아닐 가능성이 높음)
    def folding2(self, trace):
        folded_trace = []
        for activity in trace:
            if activity not in folded_trace:
                folded_trace.append(activity)
        return folded_trace'''

    def listALL(self):
        return self.traces

    def append(self, trace):
        self.traces.append(trace)

    '''def proper(self, tracePath):
        # 간단한 예로 트레이스 경로의 길이가 2 이상이면 적절하다고 가정
        return len(tracePath) >= 2'''

class TraceCluster:
    def __init__(self):
        self.clusters = {}
    
    def create(self, koTrace):
        self.clusters[koTrace] = {}
        self.clusters[koTrace]['array'] = []
        self.clusters[koTrace]['count'] = 0

    def append(self, koTrace, aTrace):
        self.clusters[koTrace]['array'].append(aTrace)
    
    
    def delete(self, trace, log):
        log.remove(trace)
    
    def count(self, koTrace):
        self.clusters[koTrace]['count'] += 1
    
    def listALL(self):
        return self.clusters
    
    def allMemberTraces(self, tracePath):
        return [trace for trace in self.clusters if KPTree().folding(trace) == tracePath]

class KPTree:
    def __init__(self):
        self.tree = None

    def create(self):
        self.tree = Node('START')

    def append(self, path):
        current_node = self.tree
        for part in path[1:]:  # 루트 노드 'A'는 이미 생성됐으므로 그 이후의 요소들만 추가
            #print(part)
            child = next((child for child in current_node.children if child.name == part), None)
            if child is None:
                child = Node(part, parent=current_node)
                #print(child)
            #else:
            #    print(child)
            current_node = child

    def listALL(self):
        return self.tree
    
    def listALL2(self):
        return self.__get_all_paths(self.tree)
    
    def __get_all_paths(self,node):
        if not node.children:
            return [[node.name]]
    
        paths = []
        for child in node.children:
            for path in self.__get_all_paths(child):
                paths.append([node.name] + path)
        return paths


def process_log_trace_selection_algorithm(PL):
    traceLoop = TraceLoop()
    traceCluster = TraceCluster()
    kpTREE = KPTree()

    # STEP 1: Clustering all the process traces in a process log dataset
    for oTrace in PL:
        koTrace = traceLoop.folding(oTrace)
        traceLoop.append(koTrace)
        traceCluster.create(koTrace)
        
        for aTrace in PL:
            kaTrace = traceLoop.folding(aTrace)
            if koTrace == kaTrace:
                traceCluster.append(aTrace)
                traceCluster.count()
                traceCluster.delete(aTrace)

    CPL = traceCluster.listALL()
    KPL = traceLoop.listALL()

    # STEP 2: Constructing a tree structured kernel process log
    kpTREE.create()
    for kTrace in KPL:
        for activity in kTrace:
            kpTREE.append(activity)

    τKPL = kpTREE.listALL()

    # STEP 3: Constructing a proper process log from the kernel process log
    PPL = []
    for tracePath in τKPL:
        if kpTREE.proper(tracePath):
            PPL.extend(traceCluster.allMemberTraces(tracePath))

    return PPL

log = LogReading('C:/Users/jdc/Documents/카카오톡 받은 파일/Process mining - material/2 Loop Example.xes')
#log = LogReading('C:/Users/jdc/Documents/카카오톡 받은 파일/Process mining - material/0 XES Example.xes')
groupArray,length = makeGroupArray(log)
groupArray = makeStringToArray(groupArray)
groupArray = makePartialArray(groupArray, [i for i in range(length)])

print(str(groupArray))
traceLoopT = TraceLoop()
for elem in groupArray:
    print(str(traceLoopT.folding(elem)))
kplTree = KPTree()
kplTree.create()
for path in groupArray:
    kplTree.append(traceLoopT.folding(path))
for pre, fill, node in RenderTree(kplTree.tree):
    print("%s%s" % (pre, node.name))
array = kplTree.listALL2()
print(array)



