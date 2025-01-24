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


def makeGroupRowDict(groupFragDict):
    groupFragRowDict = {}
    for key in groupFragDict.keys():
        groupFragRowDict[key] = len(groupFragDict[key])
    groupFragRowDict['END'] = getEndRow(groupFragDict)
    return groupFragRowDict

def getEndRow(groupFragDict):
    count = 0
    for key in groupFragDict.keys():
        count += groupFragDict[key].count('END')
    return count

def removeDuplicateDict(groupFragDict):
    nonDuplicateGroupFragDict ={}
    for key in groupFragDict.keys():
        nonDuplicateGroupFragDict[key] = list(set(groupFragDict[key]))
    return nonDuplicateGroupFragDict


def getParentNode(node, nonDuplicateGroupFragDict):
    parents = []
    for key in nonDuplicateGroupFragDict.keys():
        if node in nonDuplicateGroupFragDict[key]:
            parents.append(key)
    return parents



queue = []
completeArray = []

def processModel(node, nonDuplicateGroupFragDict, mergeArray):
        if node not in completeArray:
            for nodes in nonDuplicateGroupFragDict[node]:
                if nodes not in queue:
                    queue.append(nodes)
            printArrow(node, nonDuplicateGroupFragDict, mergeArray)
            completeArray.append(node)
        if (node != 'END') and (len(queue) != 0):
            processModel(queue.pop(0), nonDuplicateGroupFragDict, mergeArray)
            


def printArrow(node, nonDuplicateGroupFragDict, mergeArray):
    if isXOROpen(node, nonDuplicateGroupFragDict, mergeArray):
        for child in nonDuplicateGroupFragDict[node]:
            print(node + '->XOROpenGate->' + child)
    elif isANDOpen(node, nonDuplicateGroupFragDict, mergeArray):
        for child in nonDuplicateGroupFragDict[node]:
            print(node + '->ANDOpenGate->' + child)
    if isXORClose(node, nonDuplicateGroupFragDict, mergeArray):
        for parent in getParentNode(node, nonDuplicateGroupFragDict):
            print(parent + '->XORCloseGate->' + node)
    elif isANDClose(node, nonDuplicateGroupFragDict, mergeArray):
        for parent in getParentNode(node, nonDuplicateGroupFragDict):
            print(parent + '->ANDCloseGate->' + node)
    if isLinear(node,nonDuplicateGroupFragDict, mergeArray):
        print(node + '->' + nonDuplicateGroupFragDict[node][0])
    

def isLinear(node,nonDuplicateGroupFragDict, mergeArray):
    if len(nonDuplicateGroupFragDict[node]) != 1:
        return False
    if (nonDuplicateGroupFragDict[node], node) in mergeArray:
        return False
    return True

def isXOROpen(node, nonDuplicateGroupFragDict, mergeArray):
    if len(nonDuplicateGroupFragDict[node]) != 2:
        return False
    first = nonDuplicateGroupFragDict[node][0]
    second = nonDuplicateGroupFragDict[node][1]
    if (first, second) in mergeArray:
        return False
    if (second, first) in mergeArray:
        return False
    return True

def isANDOpen(node, nonDuplicateGroupFragDict, mergeArray):
    if len(nonDuplicateGroupFragDict[node]) != 2:
        return False
    first = nonDuplicateGroupFragDict[node][0]
    second = nonDuplicateGroupFragDict[node][1]
    if (first, second) not in mergeArray:
        return False
    if (second, first) not in mergeArray:
        return False
    return True

def isXORClose(node, nonDuplicateGroupFragDict, mergeArray):
    if len(getParentNode(node, nonDuplicateGroupFragDict)) != 2:
        return False
    first = getParentNode(node, nonDuplicateGroupFragDict)[0]
    second = getParentNode(node, nonDuplicateGroupFragDict)[1]
    if (first, second) in mergeArray:
        return False
    if (second, first) in mergeArray:
        return False
    return True

def isANDClose(node, nonDuplicateGroupFragDict, mergeArray):
    if len(getParentNode(node, nonDuplicateGroupFragDict)) != 2:
        return False
    first = getParentNode(node, nonDuplicateGroupFragDict)[0]
    second = getParentNode(node, nonDuplicateGroupFragDict)[1]
    if (first, second) not in mergeArray:
        return False
    if (second, first) not in mergeArray:
        return False
    return True


""" def ICNModel(groupFragRowDict, nonDuplicateGroupFragDict):
    if nonDuplicateGroupFragDict.keys() != groupFragRowDict.keys():
        print('error1')
    for node in nonDuplicateGroupFragDict.keys():
        ICNFragArray(node, groupFragRowDict, nonDuplicateGroupFragDict)


def ICNFragArray(node, groupFragRowDict, nonDuplicateGroupFragDict):
    if isChildLinear(node, nonDuplicateGroupFragDict, groupFragRowDict):
        printChildLinear(node, nonDuplicateGroupFragDict)
    if isParentLinear(node, nonDuplicateGroupFragDict, groupFragRowDict):
        printParentLinear(node, nonDuplicateGroupFragDict)
    if isANDOpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
        printANDOpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict)
    if isANDCloseGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
        printANDCloseGate(node, nonDuplicateGroupFragDict, groupFragRowDict)
    if isXOROpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
        printXOROpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict)
    if isXORCloseGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
        printXORCloseGate(node, nonDuplicateGroupFragDict, groupFragDict)
    if isLoopOpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
        printLoopOpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict)
    if isLoopCloseGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
        printLoopCloseGate(node, nonDuplicateGroupFragDict, groupFragRowDict)

#미완성이니 완성해야함
def isChildLinear(node, nonDuplicateGroupFragDict, groupFragRowDict):
    return (len(nonDuplicateGroupFragDict[node]) == 1) and (groupFragRowDict[node] == groupFragRowDict[(nonDuplicateGroupFragDict[node])[0]])

#미완성이니 완성해야함
def isParentLinear(node, nonDuplicateGroupFragDict, groupFragRowDict):
    return (len(getParentNode(node, nonDuplicateGroupFragDict)) == 1) and (groupFragRowDict[node] == getParentNode(node, nonDuplicateGroupFragDict)[0])

#미완성이니 완성해야함
def isANDOpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    if len(nonDuplicateGroupFragDict[node]) == 1:
        return False
    for child in nonDuplicateGroupFragDict[node]:
        if groupFragRowDict[node] != groupFragRowDict[child]:
            return False
    return True

#미완성이니 완성해야함
def isXOROpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    for child in nonDuplicateGroupFragDict[node]:
        if groupFragRowDict[node] <= groupFragRowDict[child]:
            return False
    return True

#미완성이니 완성해야함
def isLoopOpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    for child in nonDuplicateGroupFragDict[node]:
        if groupFragRowDict[node] < groupFragRowDict[child]:
            return True
    return False


#미완성이니 완성해야함
def isANDCloseGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    if len(getParentNode(node, nonDuplicateGroupFragDict)) == 1:
        return False
    for parent in getParentNode(node, nonDuplicateGroupFragDict):
        if groupFragRowDict[node] != groupFragRowDict[parent]:
            return False
    return True

#미완성이니 완성해야함
def isXORCloseGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    for parent in getParentNode(node, nonDuplicateGroupFragDict):
        if groupFragRowDict[node] <= groupFragRowDict[parent]:
            return False
    return True

#미완성이니 완성해야함
def isLoopCloseGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    for child in nonDuplicateGroupFragDict[node]:
        if groupFragRowDict[child] < groupFragRowDict[node]:
            return True
    return False

def printChildLinear(node, nonDuplicateGroupFragDict):
    print (str(node) + '->' + str(nonDuplicateGroupFragDict[node][0]))

def printParentLinear(node, nonDuplicateGroupFragDict):
    print (str(getParentNode(node, nonDuplicateGroupFragDict)[0]) + '->' + str(node))

def printANDOpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    for child in nonDuplicateGroupFragDict[node]:
        if (groupFragRowDict[node] == groupFragRowDict[child]):
            print (str(node) + '->ANDOpenGate->' + str(child))

def printANDCloseGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    for parent in getParentNode(node, nonDuplicateGroupFragDict):
        if (groupFragRowDict[node] == groupFragRowDict[parent]):
            print (str(parent) + '->ANDCloseGate->' + str(node))

def printXOROpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    for child in nonDuplicateGroupFragDict[node]:
        if (groupFragRowDict[node] > groupFragRowDict[child]):
            print (str(node) + '->XOROpenGate->' + str(child))

def printXORCloseGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    for parent in getParentNode(node, nonDuplicateGroupFragDict):
        if (groupFragRowDict[node] > groupFragRowDict[parent]):
            print (str(parent) + '->XORCloseGate->' + str(node))


def printLoopOpenGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    for child in nonDuplicateGroupFragDict[node]:
        if (groupFragRowDict[node] < groupFragRowDict[child]):
            print (str(node) + '->LoopOpenGate->' + str(child))
        else:
            print (str(node) + '->LoopOpenGate->' + str(child))

def printLoopCloseGate(node, nonDuplicateGroupFragDict, groupFragRowDict):
    for child in nonDuplicateGroupFragDict[node]:
        if (groupFragRowDict[child] < groupFragRowDict[node]):
            print (str(node) + '->LoopCloseGate->' + str(child))
            
        else:
            print (str(node) + '->LoopCloseGate->' + str(child)) """


#log = LogReading('C:/Users/jdc/Documents/카카오톡 받은 파일/review_example_large.xes')
#log = LogReading('C:/Users/jdc/Documents/카카오톡 받은 파일/Process mining - material/0 XES Example.xes')
log = LogReading('C:/Users/jdc/Documents/카카오톡 받은 파일/Process mining - material/0 XES Example.xes')
groupArray,length = makeGroupArray(log)
groupArray = makeStringToArray(groupArray)
groupArray = makePartialArray(groupArray, [i for i in range(length)])
groupFragmentArray = makeGroupFragmentArray(groupArray)
groupFragDict = makeGroupFragict(groupFragmentArray)
#groupFragRowDict = makeGroupRowDict(groupFragDict)
nonDuplicateGroupFragDict = removeDuplicateDict(groupFragDict)
mergeArray = [y for x in groupFragmentArray for y in x]

for elem in groupFragmentArray:
    print(elem)



#test1 = {'START': 1, 'A': 1, 'C': 1, 'E': 1, 'G': 2, 'B': 1, 'D': 1, 'F': 1}
#test2 = {'START': 2, 'A': 2, 'C': 2, 'E': 2, 'G': 1, 'B': 2, 'D': 2}

print('length : ' + str(length))
print('groupArray : ' + str(groupArray))
print('groupFragDict : ' + str(groupFragDict))
#print('groupFragRowDict : ' + str(groupFragRowDict))
print('nonDuplicateGroupFragDict : ' + str(nonDuplicateGroupFragDict))
print('mergeArray : ' + str(mergeArray))
processModel('START', nonDuplicateGroupFragDict, mergeArray)
#print(str(isANDClose('G', nonDuplicateGroupFragDict, mergeArray)))
#print('ICNModel : ' + str(ICNModel(groupFragRowDict, nonDuplicateGroupFragDict)))
#print('getParentNode : ' + str(getParentNode('C', nonDuplicateGroupFragDict)))
#print((len(nonDuplicateGroupFragDict['START']) == 1) and (groupFragRowDict['START'] == groupFragRowDict[(nonDuplicateGroupFragDict['START'])[0]]))
#ICNFragArray('N', groupFragRowDict, nonDuplicateGroupFragDict)
#ICNModel(groupFragDict, nonDuplicateGroupFragDict)
    