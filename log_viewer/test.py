'''from anytree import Node, RenderTree, find

# 주어진 배열
paths = [['START', 'A0', 'A', 'B', 'C', 'B', 'C', 'K', 'D', 'E', 'D', 'E', 'D', 'E', 'F', 'END'], ['START', 'A0', 'L', 'N', 'F', 'END']]

# 첫 번째 경로의 첫 요소를 루트 노드로 설정 (A 노드)
root = Node(paths[0][0])

# 트리 생성 함수
def add_path(root, path):
    current_node = root
    for part in path[1:]:  # 루트 노드 'A'는 이미 생성됐으므로 그 이후의 요소들만 추가
        print(part)
        child = find(current_node, lambda node: node.name == part, maxlevel=1)
        if child is None:
            child = Node(part, parent=current_node)
            print(child)
        else:
            print(child)
        current_node = child

# 배열을 돌면서 트리 구조 생성
for path in paths:
    add_path(root, path)

# 트리 출력
for pre, fill, node in RenderTree(root):
    print(f"{pre}{node.name}")'''

x = [1,2,3,1,2]

def deleteList(elem, list):
    list.remove(elem)

for elem in x[:]:
    #print('elem ' + str(elem))
    for elem2 in x[:]:
        #print('elem2 ' + str(elem2))
        if elem == elem2:
            print(elem)
            deleteList(elem, x)
            #print(str(x))
            continue
print(str(x))
