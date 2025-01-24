from django.shortcuts import render
from django.http import JsonResponse
from .utils import process_xes_log, process_json, process_json_by_group
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
def process_log(request):
    if request.method == 'POST':
        print('request : ' + str(request.POST))
        log_path = request.POST.get('logPath')  # Get the path from the request
        try:
            index = int(request.POST.get('selectedIndex'))  # Get selected index
        except:
            index = 1
        if log_path not in request.session.keys():
            print('this is first time')
            request.session['group'] = {}
            request.session['group'][log_path] = {}
            animationArray = []
            trace_array = []
            duplicatedGroupArray = []
            allGroupArray = []
            groupGraphArray = []
            traces, length = process_xes_log(log_path)  # Assuming your function accepts path data
            #print('traces : ' + str(traces))
            request.session['length'] = length
            for i in range(length):
                trace_array.append(process_json(traces,i))
                ##이름 바꾸기
                firstElementOfTraceArray = []
                infomationOfGroupArrray = []
                for elem in traces[i]:
                    firstElementOfTraceArray.append(elem[0])
                    infomationOfGroupArrray.append(elem)
                animationArray.append(firstElementOfTraceArray)
                duplicatedGroupArray.append(infomationOfGroupArrray)
            request.session[log_path] = trace_array
            if 'animation' not in request.session.keys():
                request.session['animation'] = {}
            request.session['animation'][log_path] = animationArray
            for i in duplicatedGroupArray:
                if [row[0] for row in i] not in [[row[0] for row in sub_arr] for sub_arr in allGroupArray]:
                    allGroupArray.append(i)
            print("group length : " + str(len(allGroupArray)))
            for i in allGroupArray:
                groupGraphArray.append(process_json_by_group(i))
            request.session['group'][log_path]['graph'] = groupGraphArray
            request.session['group'][log_path]['animation'] = allGroupArray
        else:
            request.session['length'] = len(request.session[log_path])
        print("log's length : " + str(request.session['length']))
        if (index == -1):
            return JsonResponse({'error': 'Invalid index', 'json length': request.session['length'], 'group length': len(request.session['group'][log_path]['animation'])})
        else:
            graph_data = (request.session[log_path])[index]
        print('log path : ' + log_path +  '\nindex : ' + str(index) + '\ngraph_data : ' + str(graph_data))
        lengthJson = {'json length' : request.session['length'], 'group length': len(request.session['group'][log_path])}
        merged = {**lengthJson, **graph_data}
        return JsonResponse(merged)
    return JsonResponse({'error': 'Invalid request'})


@csrf_exempt
def process_group(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        log_path = data['logPath']  # Get the path from the request
        print('log path: ' + log_path)
        index = int(data['groupIndex'])
        if (index == -1):
            return JsonResponse({'error': 'Invalid request'})
        animation = (request.session['group'][log_path]['animation'])[index]
        #trace = process_json_by_group(animation)
        trace = (request.session['group'][log_path]['graph'])[index]
        print('trace: ' + str(trace))
        animation = list(map(lambda x : x[0], animation))
        print('animation: ' + str(animation))
        return JsonResponse({'trace': trace,'animation': animation, 'index' : index})


def get_log_length(request):
    try:
        length = request.session['length']
    except:
        length = 0
    return JsonResponse({'length': length})

def index(request):
    return render(request, 'index.html')

def get_session_data(request):
    session_data = {}
    for key in request.session.keys():
        session_data[key] = request.session[key]
    return JsonResponse(session_data)

@csrf_exempt
def get_animation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print('request : ' + str(data))
        log_path = data['logPath']
        print('log path : ' + log_path)
        print('index : ' + data['index'])
        index = int(data['index'])
        if log_path in request.session.keys():
            if index < request.session['length'] :
                edgesArray = (request.session['animation'][log_path])[index]
                print('edgesArray : ' + str(edgesArray))
                return JsonResponse({'edges' : edgesArray})
            return JsonResponse({'error': 'Invalid index'})
        return JsonResponse({'error': 'Invalid path'})
    return JsonResponse({'error': 'Invalid request'})