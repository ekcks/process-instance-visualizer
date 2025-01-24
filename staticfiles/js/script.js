// log_viewer/static/js/script.js



const logForm = document.getElementById('logForm');
const logPathInput = document.getElementById('logPath');
const nodeSelect = document.getElementById('nodeSelect');
const layoutSelect = document.getElementById('layoutSelect');
const container = document.getElementById('graphContainer');
const startAnimationBtn = document.getElementById('startBtn');
const pauseAnimationBtn = document.getElementById('pauseBtn');
const stopAnimationBtn = document.getElementById('stopBtn');
const animationSelect = document.getElementById('animationSelect');
const groupSelect = document.getElementById('groupSelect');
const indexInput = document.getElementById('indexInput');
const traceBtn = document.getElementById('traceBtn');
const groupBtn = document.getElementById('groupBtn');
const groupIndexInput = document.getElementById('groupIndexInput');
const groupAnimationSelect = document.getElementById('groupAnimationSelect');
const groupLabel= document.getElementById('groupLabel');

let animationTimeout;
let isPaused = false;
let lastAnimationIndex;
let remainingTime1;
let bfsArray;
let indexSet;
let animationlength;
let isRemoveHighlighted = false;
let dictOfGroup = {};

/**function for animation parameter. 
 * When elements are already highlighted, turn off highlight and make highlighted again.
 * If not, make highlight and move on next element. 
 * @param {number} i index for highlighting @param {Object[]} bfs array of cytoscape.js elements want to animate */
var highlightNextEle = function (i, bfs) {
    if (i < bfs.length) {
        console.log('hasClass : ' + bfs[i].hasClass('highlighted'));
        if (isRemoveHighlighted) { // when it has to be repeated
            bfs[i].addClass('highlighted');
            bfs[i].removeClass('unhighlighted');
            console.log('add highlight ' + bfs[i].id());
            i++; // add 1 to index(next element)
            isRemoveHighlighted = false;
            }
        else {
            if (bfs[i].hasClass('highlighted')) { // when it is already highlighted( ex) A in A->C->A )
                bfs[i].addClass('unhighlighted');
                bfs[i].removeClass('highlighted');
                console.log('remove highlight ' + bfs[i].id()); // without add 1 to index (unhighlighted to highlighted again)
                isRemoveHighlighted = true;
            }
            else {
                bfs[i].addClass('highlighted');
                console.log('add highlight ' + bfs[i].id());
                i++; // add 1 to index(next element)
            };
        }
    }
    else { // when animation has to be stopped
        lastAnimationIndex = 0;
        return;
    }
    lastAnimationIndex = i; // remember last animated index
    console.log('i :' + i);
    animationTimeout = setTimeout(function () {
        highlightNextEle(i, bfs);
    }, 1000); // repeat every 1 second.
}
    

/**function for starting animation 
 * When the animation is paused, then start it again.
*/
function startAnimation() {
    if (isPaused) {
        isPaused = false;
        animationTimeout = setTimeout(function () {
            highlightNextEle(lastAnimationIndex, bfsArray); // start with last animated index element
        }, remainingTime1);
    }
    else {
        highlightNextEle(0, bfsArray); // start animation with start node
    };
}

/**function for pausing animation */
function pauseAnimation() {
    clearTimeout(animationTimeout);
    remainingTime1 = animationTimeout._idleTimeout;
    isPaused = true;
}

/**function for stopping animation */
function stopAnimation() {
    // clear the current animation timeout and remove highlights of all elements
    clearTimeout(animationTimeout);
    if (container.children.length != 0) container._cyreg.cy.elements().removeClass('highlighted');
    if (container.children.length != 0) container._cyreg.cy.elements().removeClass('unhighlighted');
    isPaused = false;
}

/**function for rendering group. 
 * When the container is empty, make new graph
 * When not, mege two graph into one(weights of edges are added)
 * then, make variable 'bfsArray' blank and make animation array then put into variable 'bfsArray'
 * @param {JSON} groupData json format data consist of graph data and animation data */
function renderGroup(groupData) {
    if (groupData['error'] == 'Invalid request')
        return null;
    graph = groupData['trace'];
    animationGroupArray = groupData['animation'];
    index = groupData['index'];
    if (container.children.length == 0) {
        dictOfGroup = {};
        console.log('there\' s no graph/Group');
        const cy = cytoscape({
            container: container,
            elements: graph.elements, 
            style: cytoscape.stylesheet()
                .selector('node')
                .style({
                    'background-color': '#666',
                    'label': 'data(event_name)'
                })
                .selector('edge')
                .style({
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'width': 3,
                    'line-color': '#ccc',
                    'target-arrow-color': '#000',
                    'label': 'data(weight)'
                })
                .selector('.highlighted') //for highlighting
                .style({
                    'background-color': '#61bffc',
                    'line-color': '#61bffc',
                    'target-arrow-color': '#61bffc',
                    'transition-property': 'background-color, line-color, target-arrow-color',
                    'transition-duration': '0.5s'
                })
                .selector('.unhighlighted') //for unhighlighting
                .style({
                    'background-color': '#666',
                    'line-color': '#ccc',
                    'target-arrow-color': '#000',
                    'transition-property': 'background-color, line-color, target-arrow-color',
                    'transition-duration': '0.5s'
                }),
        });
        cy.elements().forEach((elem) => elem.data('trace_list', [index])); // mark their trace number
    }
    else {
        const cyt = container._cyreg.cy;
        // merge Cytoscape instance into one
        const cy = cytoscape({
            elements: graph.elements, 
            style: cytoscape.stylesheet()
                .selector('node')
                .style({
                    'background-color': '#666',
                    'label': 'data(event_name)'
                })
                .selector('edge')
                .style({
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'width': 3,
                    'line-color': '#ccc',
                    'target-arrow-color': '#000',
                    'label': 'data(weight)'
                })
                .selector('.highlighted')
                .style({
                    'background-color': '#61bffc',
                    'line-color': '#61bffc',
                    'target-arrow-color': '#61bffc',
                    'transition-property': 'background-color, line-color, target-arrow-color',
                    'transition-duration': '0.5s'
                }),
        });
        cy.elements().forEach((elem) => elem.data('trace_list', [index]));

        console.log('there\'s graph/Group');
        // Add nodes from cyt instance to cy in container if they don't already exist in cy based on ID
        cy.nodes().forEach((node) => {
            const existingNode = cyt.getElementById(node.id());
            console.log('existingNode == null : ' + (existingNode == null));
            if (existingNode.data('id') != undefined) {
                // Merge 'trace_list' arrays
                console.log('node.id : ' + node.data('id'));
                console.log('exstingNode.id : ' + existingNode.data('id'));
                console.log('exstingNode.trace_list : ' + existingNode.data('trace_list'));
                const mergedTraceList = [...new Set(existingNode.data('trace_list').concat(node.data('trace_list')))];
                existingNode.data('trace_list', mergedTraceList);
            } else {
                cyt.add(node);
            }
        });
        // Add edges from cyt instance to cy in container if they don't already exist in cy based on source node and target node
        cy.edges().forEach((edge) => {
            const sourceId = edge.source().id();
            const targetId = edge.target().id();
            const existingEdge = cyt.edges().filter((e) => e.source().id() === sourceId && e.target().id() === targetId);
            if (existingEdge.length === 1) {
                // Merge 'trace_list' arrays
                const mergedTraceList = [...new Set(existingEdge[0].data('trace_list').concat(edge.data('trace_list')))];
                existingEdge[0].data('trace_list', mergedTraceList);

                // Sum the 'weight' properties
                const newWeight = existingEdge[0].data('weight') + edge.data('weight');
                existingEdge[0].data('weight', newWeight);

                // Update label to new weight
                existingEdge[0].data('label', newWeight);
            } else {
                cyt.add(edge);
            }
            cyt.style()
                .selector('edges')
                .style({ 'label': 'data(weight)' })
                .update();
        });

    };

    let options = {
        name: layoutSelect.value,
        directed: true,
        roots: '#START',
        padding: 10
    }

    container._cyreg.cy.layout(options).run();
    container._cyreg.cy.fit();
    // add functions to display its id to nodes and edges
    container._cyreg.cy.on('tap', 'node', function (evt) {
        window.alert('clicked node : ' + this.data('event_name') + '\nclicked node performer : ' + this.data('performer_name') + '\nclicked node timestamp : ' + this.data('time_stamp'));
    });
    container._cyreg.cy.on('tap', 'edge', function (evt) {
        window.alert('clicked edge : ' + this.data('source') + '->' + this.data('target') + '\nclicked edge weight : ' + this.data('weight'));
    });
    bfsArray = [];
    findGraphPath(animationGroupArray);
    const cyt = container._cyreg.cy;
    console.log('bfsArray : ' + bfsArray);
    console.log('cy : ' + container._cyreg.cy);
    console.log('cy.layout' + container._cyreg.cy.layout);
    dictOfGroup[index] = animationGroupArray;
}

/**function for merging and rendering
 * When the container is empty, make new graph
 * When not, mege two graph into one(weights of edges are added)
 *  @param {JSON} graphData cytoscape json format of xes log @param {number} index index of graph in xes log */
function renderGraph(graphData, index) {
    if (container.children.length == 0) {
        console.log('there\' s no graph');
        // Create a new Cytoscape instance
        const cy = cytoscape({
            container: container,
            elements: graphData.elements, 
            style: cytoscape.stylesheet()
                .selector('node')
                .style({
                    'background-color': '#666',
                    'label': 'data(event_name)'
                })
                .selector('edge')
                .style({
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'width': 3,
                    'line-color': '#ccc',
                    'target-arrow-color': '#000',
                    'label': 'data(weight)'
                })
                .selector('.highlighted') //for highlighting
                .style({
                    'background-color': '#61bffc',
                    'line-color': '#61bffc',
                    'target-arrow-color': '#61bffc',
                    'transition-property': 'background-color, line-color, target-arrow-color',
                    'transition-duration': '0.5s'
                })
                .selector('.unhighlighted') //for unhighlighting
                .style({
                    'background-color': '#666',
                    'line-color': '#ccc',
                    'target-arrow-color': '#000',
                    'transition-property': 'background-color, line-color, target-arrow-color',
                    'transition-duration': '0.5s'
                }),
        });
        cy.elements().forEach((elem) => elem.data('trace_list', [index])); // mark their trace number 

    }
    else {
        const cyt = container._cyreg.cy;
        // merge Cytoscape instance into one
        const cy = cytoscape({
            elements: graphData.elements, 
            style: cytoscape.stylesheet()
                .selector('node')
                .style({
                    'background-color': '#666',
                    'label': 'data(event_name)'
                })
                .selector('edge')
                .style({
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'width': 3,
                    'line-color': '#ccc',
                    'target-arrow-color': '#000',
                    'label': 'data(weight)'
                })
                .selector('.highlighted')
                .style({
                    'background-color': '#61bffc',
                    'line-color': '#61bffc',
                    'target-arrow-color': '#61bffc',
                    'transition-property': 'background-color, line-color, target-arrow-color',
                    'transition-duration': '0.5s'
                }),
        });
        cy.elements().forEach((elem) => elem.data('trace_list', [index]));

        console.log('there\'s graph');
        // Add nodes from cyt instance to cy in container if they don't already exist in cy based on ID
        cy.nodes().forEach((node) => {
            const existingNode = cyt.getElementById(node.id());
            console.log('existingNode == null : ' + (existingNode == null));
            if (existingNode.data('id') != undefined) {
                // Merge 'trace_list' arrays
                console.log('node.id : ' + node.data('id'));
                console.log('exstingNode.id : ' + existingNode.data('id'));
                console.log('exstingNode.trace_list : ' + existingNode.data('trace_list'));
                const mergedTraceList = [...new Set(existingNode.data('trace_list').concat(node.data('trace_list')))];
                existingNode.data('trace_list', mergedTraceList);
            } else {
                cyt.add(node);
            }
        });
        // Add edges from cyt instance to cy in container if they don't already exist in cy based on source node and target node
        cy.edges().forEach((edge) => {
            const sourceId = edge.source().id();
            const targetId = edge.target().id();
            const existingEdge = cyt.edges().filter((e) => e.source().id() === sourceId && e.target().id() === targetId);
            if (existingEdge.length === 1) {
                // Merge 'trace_list' arrays
                const mergedTraceList = [...new Set(existingEdge[0].data('trace_list').concat(edge.data('trace_list')))];
                existingEdge[0].data('trace_list', mergedTraceList);

                // Sum the 'weight' properties
                const newWeight = existingEdge[0].data('weight') + edge.data('weight');
                existingEdge[0].data('weight', newWeight);

                // Update label to new weight
                existingEdge[0].data('label', newWeight);
            } else {
                cyt.add(edge);
            }
            cyt.style()
                .selector('edges')
                .style({ 'label': 'data(weight)' })
                .update();
        });

    };

    let options = {
        name: layoutSelect.value,
        directed: true,
        roots: '#START',
        padding: 10
    }

    container._cyreg.cy.layout(options).run();
    container._cyreg.cy.fit();
    // add functions to display its id to nodes and edges
    container._cyreg.cy.on('dbltap', 'node', function (evt) {
        window.alert('clicked node : ' + this.data('event_name') + '\nclicked node performer : ' + this.data('performer_name') + '\nclicked node timestamp : ' + this.data('time_stamp'));
    });
    container._cyreg.cy.on('dbltap', 'edge', function (evt) {
        window.alert('clicked edge : ' + this.data('source') + '->' + this.data('target') + '\nclicked edge weight : ' + this.data('weight'));
    });

    console.log('cy : ' + container._cyreg.cy);
    console.log('cy.layout' + container._cyreg.cy.layout);
};


/**function for fetch to server for graph 
 * When fetch is finished, then add <index>tag indexInput to website or clean <index>tag indexInput
 * @param {number} index index of xes log */
function fetchgraph(index) {
    const formData = new FormData(logForm);
    const selectedIndex = index; // Get the selected index
    formData.append('selectedIndex', selectedIndex); // Append selected index to form data
    const logPath = logPathInput.value; // Get the path from the input field
    formData.append('logPath', logPath); // Append path to form data
    fetch('/process_log/', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log('data : ' + data);
            length = data['json length'];
            groupLength = data['group length']
            animationlength = length;
            console.log('json length : ' + length);
            console.log('group length : ' + groupLength);
            if (data.error == 'Invalid index') console.log('Invalid index');
            else { // Call fetchLogLength and wait for it to complete
                renderGraph(data, index); // Render graph after fetchLogLength completes
            };
        })
        .then(data => {
            if (groupSelect.value = -1 && groupSelect.children.length == 1){
                makeGroupSelectTagWithNumber(groupLength);
                for(i = 0; i < groupLength; i++){
                    const option1 = document.createElement('option');
                    option1.value = i;
                    option1.textContent = 'Group ' + i;
                    groupSelect.appendChild(option1);
                }
            }
        })
        .then(data => { 
            if (indexInput.style.display = 'none') { // display invisible <input>tag indexInput if it's invisible

                indexInput.style.display = 'inline';
                indexInput.placeholder = 'index: 0~' + (length - 1);
                indexInput.value = '';
            }
            else { // clear <input>tag indexInput if it's visible
                indexInput.placeholder = 'index: 0~' + (length - 1);
                indexInput.value = '';
            }

            if (groupIndexInput.style.display = 'none') { // display invisible <input>tag groupIndexInput if it's invisible

                groupIndexInput.style.display = 'inline';
                groupIndexInput.placeholder = 'group: 0~' + (groupLength - 1);
                groupIndexInput.value = '';
            }
            else { // clear <input>tag groupIndexInput if it's visible
                groupIndexInput.placeholder = 'group: 0~' + (groupLength - 1);
                groupIndexInput.value = '';
            }
        })
        .catch(error => console.error('Error processing log:', error));
};


/**function for clearing and setting <select>tag animationSelect to initial value */
function makeAnimationSelectTag() {
    animationSelect.innerHTML = ''; // Clear existing options
    const option1 = document.createElement('option');
    option1.value = -1;
    option1.textContent = `Animate Trace`;
    animationSelect.appendChild(option1);
};


/**function for clearing and setting <select>tag groupSelect to initial value */
function makeGroupSelectTag() {
    groupSelect.innerHTML = ''; // Clear existing options
    const option1 = document.createElement('option');
    option1.value = -1;
    option1.textContent = `Group of traces`;
    groupSelect.appendChild(option1);
};

/**function for clearing and setting <select>tag groupSelect to initial value with number of groups
 * @param {number} number number of group
*/
function makeGroupSelectTagWithNumber(number) {
    groupSelect.innerHTML = ''; // Clear existing options
    const option1 = document.createElement('option');
    option1.value = -1;
    option1.textContent = `Group of traces(count:` + number + ')';
    groupSelect.appendChild(option1);
};

/**function for adding selected index of trace in xes log to <select>tag animationSelect 
 * @param {number} index index of graph you choose on <input>tag indexInput  */
function addAnimationSelectTag(index) {
    const option1 = document.createElement('option');
    option1.value = Number(index);
    option1.textContent = 'Trace ' + index;
    animationSelect.appendChild(option1);
}

/**function for clearing and setting <select>tag groupAnimationSelect to initial value */
function makeGroupAnimationSelectTag() {
    groupAnimationSelect.innerHTML = ''; // Clear existing options
    const option1 = document.createElement('option');
    option1.value = -1;
    option1.textContent = `Animate Trace`;
    groupAnimationSelect.appendChild(option1);
};


/**function for fetch to server for graph when you use <input>tag indexInput 
 * it slice input value by comma, and if there's input with -, then slice it by - too
 * then, make array of input integer and sort
*/
function fetchgraphforInput() {
    makeAnimationSelectTag();
    let indexInputArray = indexInput.value.split(','); // merge input value by comma
    indexSet = new Set();
    indexInputArray.forEach((elem) => {
        console.log(elem);
        if (elem.includes('-')) { // if there's - in input element ex) 5-10
            startNumber = Number(elem.split('-')[0]); // start : 5
            endNumber = Number(elem.split('-')[1]); // start : 10
            for (let index = startNumber; index <= endNumber; index++) {
                indexSet.add(index); // indexSet = [5,6,7,8,9,10]
            }
        }
        else {
            indexSet.add(Number(elem));
        }
    });
    indexSet = new Set(Array.from(indexSet).sort(function (a, b) { // sort array
        return a - b;
    }));

    indexSet.forEach((elem) => {
        console.log('type of ' + elem + ' : ' + typeof (elem) + '/' + (elem + 1));
        addAnimationSelectTag(elem);
        fetchgraph(elem);
    });
    console.log('finished!');
}


/**function for fetch to server for graph when you use <input>tag groupIndexInput 
 * it slice input value by comma, and if there's input with -, then slice it by - too
 * then, make array of input integer and sort
*/
function fetchgraphforGroupInput() {
    makeGroupAnimationSelectTag();
    let indexInputArray = groupIndexInput.value.split(','); // merge input value by comma
    indexSet = new Set();
    indexInputArray.forEach((elem) => {
        console.log(elem);
        if (elem.includes('-')) { // if there's - in input element ex) 5-10
            startNumber = Number(elem.split('-')[0]); // start : 5
            endNumber = Number(elem.split('-')[1]); // start : 10
            for (let index = startNumber; index <= endNumber; index++) {
                indexSet.add(index); // indexSet = [5,6,7,8,9,10]
            }
        }
        else {
            indexSet.add(Number(elem));
        }
    });
    indexSet = new Set(Array.from(indexSet).sort(function (a, b) { // sort array
        return a - b;
    }));
    console.log(indexSet);
    let fetchPromises = [];
    indexSet.forEach((elem) => {
        console.log('type of ' + elem + ' : ' + typeof (elem) + '/' + (elem + 1));
        addGroupAnimationSelectTag(elem);
        fetchPromises.push(fetchGroupGraph(elem));
    });
    Promise.all(fetchPromises).then(() => {
        alertInfoOfGroup();
    });
    console.log('finished!');
}

/**function for alerting infomation of group
 * the infomation consist of index of group and path of group
 */
function alertInfoOfGroup() {
    let textOfGroupInfo = [];
    for(value in dictOfGroup){
        let text = 'Group ' + value + ": " + dictOfGroup[value].join('->');
        textOfGroupInfo.push(text);
    }
    groupLabel.innerHTML = textOfGroupInfo.join('<br/><br/>');
    //groupLabel.innerHTML = JSON.stringify(dictOfGroup);
    //alert(JSON.stringify(dictOfGroup));
}


/**function for fetch to server for graph 
 * When fetch is finished, then add <index>tag groupIndexInput to website or clean <index>tag groupIndexInput
 * @param {number} index index of xes log */
function fetchGroupGraph(index) {
    return new Promise((resolve, reject) => {
        
        const formData = new FormData(logForm);
        const selectedIndex = index; // Get the selected index
        formData.append('selectedIndex', selectedIndex); // Append selected index to form data
        const logPath = logPathInput.value; // Get the path from the input field
        formData.append('logPath', logPath); // Append path to form data
        fetch('/process_group/', {
            method: 'POST',
            body: JSON.stringify({
                'logPath': logPathInput.value,
                'groupIndex': selectedIndex,
              }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('data : ' + data);
            animation = data['animation'];
            index = data['index']
            console.log('path : ' + animation);
            console.log('index : ' + index);
            if (data.error == 'Invalid index') {
                console.log('Invalid index');
                reject('Invalid index');
            }
            else { // Call fetchLogLength and wait for it to complete
                renderGroup(data); // Render graph after fetchLogLength completes
                resolve(data);
                };
        })
        .then(data => { 
            if (groupIndexInput.style.display = 'none') { // display invisible <input>tag indexInput if it's invisible

                groupIndexInput.style.display = 'inline';
                groupIndexInput.placeholder = 'index: 0~' + (length - 1);
                groupIndexInput.value = '';
            }
            else { // clear <input>tag indexInput if it's visible
                groupIndexInput.placeholder = 'index: 0~' + (length - 1);
                groupIndexInput.value = '';
                }
        })
        .catch(error => {
            console.error('Error processing log:', error);
            reject(error);
        });
    });
}

/**function for adding selected index of group in xes log to <select>tag groupAnimationSelect 
 * @param {number} index index of graph you choose on <input>tag indexInput  */
function addGroupAnimationSelectTag(index) {
    const option1 = document.createElement('option');
    option1.value = Number(index);
    option1.textContent = 'Group ' + index;
    groupAnimationSelect.appendChild(option1);
}


/**function for finding path for animation 
 * it finds animation path by order of value stored in django sessions.
 * @param {string[]} array array of name of elements saved on sessions */
function findGraphPath(array) {
    console.log('findGraphArray  : ' + array);
    array.forEach(elem => console.log(elem));
    if (container.children.length != 0){
        const cyt = container._cyreg.cy;
        bfsArray = [];
        bfsArray.push(cyt.getElementById('START')); // START node is first
        for (let index = 1; index < array.length; index++){
            const existingEdge = cyt.edges().filter((e) => e.source().id() === array[index-1] && e.target().id() === array[index]); // next edge : (START -> A)
            bfsArray.push(existingEdge[0]); // add edge (START -> A)
            const existingNode = cyt.getElementById(array[index]);
            bfsArray.push(existingNode); // add node A
        }
    };
}



//functions for loading webpage
document.addEventListener('DOMContentLoaded', function () {
    sessionStorage.clear();
    logForm.addEventListener('submit', function (event) {
        event.preventDefault();
        fetchgraph(-1);
        traceBtn.disabled = false;
        groupBtn.disabled = false;
    });

    logPathInput.addEventListener('change', function () {
        stopAnimation();
        // Clear previous graph
        container.innerHTML = '';
        groupLabel.innerHTML = '';
        bfsArray = [];
        makeGroupSelectTag();
        makeAnimationSelectTag();
        logForm.dispatchEvent(new Event('submit'));
    });

    nodeSelect.addEventListener('change', function (event) {
        console.log('Node selection changed:', event.target.value); // Log the selected value to check if the event is firing
        const cyt = document.getElementById('graphContainer')._cyreg.cy;
        if (cyt == null) {
            console.log('Null Graph');
        } else {
            const selectedAttribute = nodeSelect.value;
            console.log('Selected attribute :', selectedAttribute); // Log the selected attribute to ensure it's correct
            cyt.nodes().forEach(function (node) {
                const label = node.data(selectedAttribute); // Get the value of the selected attribute
                node.data('label', label); // Set the node's label to the attribute value
                console.log('Node label :', node.data(selectedAttribute)); // Log the label to ensure it's correct
            });
            cyt.style()
                .selector('node')
                .style({ 'label': 'data(label)' }) // Update style with the new labels
                .update(); // Update the style to reflect the changes
        }
    });

    layoutSelect.addEventListener('change', function (event) {
        console.log('layout selection changed:', event.target.value); // Log the selected value to check if the event is firing
        const cyt = document.getElementById('graphContainer')._cyreg.cy;
        if (cyt == null) {
            console.log('Null Graph');
        } else {
            const selectedAttribute = layoutSelect.value;
            console.log('Selected layout attribute :', selectedAttribute); // Log the selected attribute to ensure it's correct
            cyt.layout({
                name: selectedAttribute,
                directed: true,
                roots: '#START',
                padding: 10
            }).run();
        }
    });

    animationSelect.addEventListener('change', function (event) {
        fetch("/get_animation/", {
            method: "POST",
            body: JSON.stringify({
              'logPath': logPathInput.value,
              'index': animationSelect.value,
            }),
          })
          .then((response) => response.json())
          .then((result) => findGraphPath(result['edges']));
        stopAnimation();
    });
    startAnimationBtn.addEventListener('click', startAnimation);
    pauseAnimationBtn.addEventListener('click', pauseAnimation);
    stopAnimationBtn.addEventListener('click', stopAnimation);

    indexInput.addEventListener('change', function (event) {
        container.innerHTML = '';
        groupLabel.innerHTML = '';
        fetchgraphforInput();
    });

    groupSelect.addEventListener('change', function (event) {
        stopAnimation();
        container.innerHTML = '';
        animationSelect.value = '';
        indexInput.value = '';
        groupLabel.innerHTML = '';
        bfsArray = [];
        console.log('logPath: ' + logPathInput.value);
        console.log('groupIndex: ' + groupSelect.value);
        fetch("/process_group/", {
            method: "POST",
            body: JSON.stringify({
              'logPath': logPathInput.value,
              'groupIndex': groupSelect.value,
            }),
          })
          .then((response) => response.json())
          .then((result) => renderGroup(result));
    });
    
    traceBtn.addEventListener('click', function () {
        stopAnimation();
        container.innerHTML = '';
        groupLabel.innerHTML = '';
        if (indexInput.display != 'none')
            indexInput.disabled = false;
        makeAnimationSelectTag();
        animationSelect.disabled = false;
        groupSelect.disabled = true;
        groupIndexInput.disabled = true;
        groupAnimationSelect.disabled = true;
        groupSelect.value = -1;
    });
    groupBtn.addEventListener('click', function () {
        stopAnimation();
        container.innerHTML = '';
        groupLabel.innerHTML = '';
        if (indexInput.display != 'none')
            indexInput.disabled = true;
        animationSelect.disabled = true;
        groupSelect.value = -1;
        groupSelect.disabled = false;
        groupIndexInput.disabled = false;
        groupAnimationSelect.disabled = false;
    });

    groupIndexInput.addEventListener('change', function (event) {
        container.innerHTML = '';
        groupLabel.innerHTML = '';
        fetchgraphforGroupInput();
    });


    groupAnimationSelect.addEventListener('change', function (event) {
        fetch("/process_group/", {
            method: "POST",
            body: JSON.stringify({
              'logPath': logPathInput.value,
              'groupIndex': groupAnimationSelect.value,
            }),
          })
          .then((response) => response.json())
          .then((result) => findGraphPath(result['animation']));
        stopAnimation();
    });

    makeAnimationSelectTag();
    makeGroupSelectTag();
    indexInput.style.display = 'none';
    groupIndexInput.style.display = 'none';
});
