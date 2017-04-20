import { Map, fromJS } from 'immutable';

export const FETCH_META_GRAPH = 'FETCH_META_GRAPH';
export const FETCHED_META_GRAPH = 'FETCHED_META_GRAPH';
export const MARK_DISPLAY_NODE = 'MARK_DISPLAY_NODE';
export const MARK_DISPLAY_LINK = 'MARK_DISPLAY_LINK';
export const TOGGLE_NODE_TO_SELECTED_GRAPH = 'ADD_NODE_TO_SELECTED_GRAPH';
export const TOGGLE_LINK_TO_SELECTED_GRAPH = 'ADD_LINK_TO_SELECTED_GRAPH';
export const POST_GRAPH_RULE = 'POST_GRAPH_RULE';
export const POSTED_GRAPH_RULE = 'POSTED_GRAPH_RULE';
export const FETCHED_GRAPH_RULE = 'FETCHED_GRAPH_RULE';
export const FETCH_GRAPH_RULE = 'FETCH_GRAPH_RULE';

const initialState = Map({
  metaGraph: Map({}),
  displayGraph: Map({
    nodes: [],
    links: []
  }),
  selectedGraph: {
    nodes: [],
    links: []
  }
});
export default function reducer(state = initialState, action) {
  switch (action.type) {
    case FETCHED_META_GRAPH:
      return fromJS(setGraphs(state, action.payload));

    case TOGGLE_NODE_TO_SELECTED_GRAPH:
      return fromJS(toggleNode(state, action.payload));
    case TOGGLE_LINK_TO_SELECTED_GRAPH:
      return fromJS(toggleLink(state, action.payload));
    case MARK_DISPLAY_NODE:
      return fromJS(markDisplayNode(state, action.payload));
    case MARK_DISPLAY_LINK:
      return fromJS(markDisplayLink(state, action.payload));
    case POSTED_GRAPH_RULE:
      return fromJS(markDisplayGraph(state, action.payload));
    case FETCHED_GRAPH_RULE:
      return fromJS(markDisplayGraph(state, action.payload));
    default:
      return state;
  }
}
export function toggleNodeToSelectedGraph(payload) {
  return { type: TOGGLE_NODE_TO_SELECTED_GRAPH, payload };
}
export function toggleLinkToSelectedGraph(payload) {
  return { type: TOGGLE_LINK_TO_SELECTED_GRAPH, payload };
}
export function getMetaGraph() {
  return { type: FETCH_META_GRAPH };
}

export function selectDisplayNode(payload) {
  return { type: MARK_DISPLAY_NODE, payload };
}
export function selectDisplayLink(payload) {
  return { type: MARK_DISPLAY_LINK, payload };
}
export function postNewRule(payload) {
  return { type: POST_GRAPH_RULE, payload };
}
export function getNewRule(payload) {
  return { type: FETCH_GRAPH_RULE, payload };
}

function toggleNode(oldState, payload) {
  let newState = oldState.toJS();

  //look for node and index:
  let node = newState.selectedGraph.nodes.find(x => {
    return x.id === payload.item.id;
  });
  let i = newState.selectedGraph.nodes.indexOf(node);

  //add if not present and return:
  if (i === -1) {
    newState.selectedGraph.nodes.push(payload.item);
    return newState;
  }
  //else remove:
  newState.selectedGraph.nodes.splice(i, 1);
  return newState;
}

function toggleLink(oldState, payload) {
  console.log('payload: ');
  console.log(payload);
  let newState = oldState.toJS();
  //get the link obj from displaygraph
  let linkFromDisplay = newState.displayGraph.links.find(link => {
    return (
      link.source === payload.source.index &&
      link.target === payload.target.index
    );
  });
  console.log('displaygraph: ');
  console.log(linkFromDisplay);

  //look for node and index:
  let link = newState.selectedGraph.links.find(x => {
    return (
      x.source === payload.source.index && x.target === payload.target.index
    );
  });
  console.log('selectedGraph: ');
  console.log(link);

  let i = newState.selectedGraph.links.indexOf(link);
  //  console.log(i);
  //console.log(link);
  // console.log(payload);
  //add if not present and return:
  if (i === -1) {
    newState.selectedGraph.links.push(linkFromDisplay);
    return newState;
  }
  //else remove
  newState.selectedGraph.links.splice(i, 1);
  return newState;
}

function markDisplayNode(oldState, payload) {
  let newState = oldState.toJS();

  let node = newState.displayGraph.nodes.find(x => {
    return x.name === payload;
  });
  node.marked = !node.marked;
  return newState;
}

function markDisplayLink(oldState, payload) {
  let newState = oldState.toJS();

  newState.displayGraph.links.forEach(x => {
    if (
      x.source === payload.source.index && x.target === payload.target.index
    ) {
      x.marked = !x.marked;
    }
  });
  return newState;
}

function markDisplayGraph(oldState, payload) {
  console.log(payload);
  let newState = oldState.toJS();

  if (newState.displayGraph.nodes.length === 0) {
    return newState;
  }
  //  console.log(payload);

  const SOURCE = payload.ctype_source.substr(
    payload.ctype_source.indexOf('.') + 1
  );
  const TARGET = payload.ctype_target.substr(
    payload.ctype_target.indexOf('.') + 1
  );
  const RELATIONS = payload.relation_types;

  console.log(newState.selectedGraph.nodes.length);

  //TODO: clean up this mess.....
  if (newState.selectedGraph.nodes.length === 0) {
    //add source node if selectedgraph is empty
    newState.displayGraph.nodes.forEach(node => {
      if (node.label.toLowerCase() === SOURCE.toLowerCase()) {
        node.marked = true;

        if (newState.selectedGraph.nodes[0] === undefined) {
          newState.selectedGraph.nodes.push(node.item);
          let nodeId = newState.displayGraph.nodes.indexOf(node);
          let l = newState.displayGraph.links.find(x => {
            return RELATIONS[0] === x.type && x.source === nodeId;
          });
          l.marked = 1;
          newState.selectedGraph.links.push(l);
        }
      }
    });

    newState.displayGraph.nodes.forEach(node => {
      if (node.label.toLowerCase() === TARGET.toLowerCase()) {
        node.marked = true;

        //here is bug:

        if (
          newState.selectedGraph.nodes[0] !== undefined &&
          newState.selectedGraph.nodes[newState.selectedGraph.nodes.length - 1]
            .model_name !== node.item.model_name
        ) {
          newState.selectedGraph.nodes.push(node.item);
          console.log('jjj');
        }
      }
    });
  }
  //console.log(newState);
  return newState;
}

function setGraphs(oldState, payload) {
  let newState = oldState.toJS();

  let displayGraph = {
    nodes: [],
    links: []
  };
  newState.metaGraph = payload;

  //add nodes
  newState.metaGraph.forEach((value, key, map) => {
    displayGraph.nodes.push({
      name: value.label,
      label: value.label,
      id: value.id,
      marked: false,
      hoover: false,
      item: value
    });
  });

  //add links
  newState.metaGraph.forEach((value, key, map) => {
    let index = key;
    Object.values(value).forEach((property, key, map) => {
      if (typeof property === 'object' && !property[1]) {
        let target = displayGraph.nodes.filter(x => {
          if (x.name === property[0].to) {
            return x;
          }
        });

        displayGraph.links.push({
          source: index,
          target: displayGraph.nodes.indexOf(target[0]),
          type: property[0].relation_type,
          linkShape: 0,
          marked: false,
          hoover: false
        });
      }
    });
  });

  //add factor for duplicate source and target
  displayGraph.links.forEach((value, key, map) => {
    if (value.linkShape !== 0) return;

    let a = displayGraph.links.filter(l => {
      return value.source === l.source && l.target === value.target;
    });
    let incr = 0;
    a.forEach((value, key, map) => {
      value.linkShape = incr;
      incr += 150;
    });
  });

  newState.displayGraph = displayGraph;
  return newState;
}
