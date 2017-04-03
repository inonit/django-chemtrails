import { Map, fromJS } from 'immutable';

export const FETCH_META_GRAPH = 'FETCH_META_GRAPH';
export const FETCHED_META_GRAPH = 'FETCHED_META_GRAPH';
export const MARK_DISPLAY_NODE = 'MARK_DISPLAY_NODE';
export const MARK_DISPLAY_LINK = 'MARK_DISPLAY_LINK';
export const ADD_NODE_TO_SELECTED_GRAPH = 'ADD_NODE_TO_SELECTED_GRAPH';
export const ADD_LINK_TO_SELECTED_GRAPH = 'ADD_LINK_TO_SELECTED_GRAPH';

const initialState = Map({
  metaGraph: Map({}),
  displayGraph: {
    nodes: [],
    links: []
  },
  selectedGraph: {
    nodes: [],
    links: []
  }
});
export default function reducer(state = initialState, action) {
  switch (action.type) {
    case FETCHED_META_GRAPH:
      return fromJS(setGraphs(state, action.payload));
    case MARK_DISPLAY_NODE:
      return fromJS(markDisplayNode(state, action.payload));
    case ADD_NODE_TO_SELECTED_GRAPH:
      return fromJS(addNode(state, action.payload));
    case ADD_LINK_TO_SELECTED_GRAPH:
      return fromJS(addLink(state, action.payload));
    case MARK_DISPLAY_NODE:
      return fromJS(markDisplayNode(state, action.payload));
    case MARK_DISPLAY_LINK:
      return fromJS(markDisplayLink(state, action.payload));
    default:
      return state;
  }
}
export function addNodeToSelectedGraph(payload) {
  return { type: ADD_NODE_TO_SELECTED_GRAPH, payload };
}
export function addLinkToSelectedGraph(payload) {
  return { type: ADD_LINK_TO_SELECTED_GRAPH, payload };
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

function addNode(oldState, payload) {
  let newState = oldState.toJS();
  newState.selectedGraph.nodes.push(payload);
  return newState;
}
function addLink(oldState, payload) {
  let newState = oldState.toJS();
  newState.selectedGraph.links.push(payload);
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

  let link = newState.displayGraph.links.find(x => {
    return x.name === payload;
  });
  link.marked = !link.marked;
  return newState;
}

function setGraphs(oldState, payload) {
  let newState = oldState.toJS();
  newState.metaGraph = payload;
  let g = {
    nodes: [],
    links: []
  };

  newState.metaGraph.forEach((value, key, map) => {
    g.nodes.push({
      name: value.label,
      label: value.label,
      id: value.id,
      marked: 0,
      hoover: 0,
      item: value
    });
  });

  newState.metaGraph.forEach((value, key, map) => {
    let index = key;
    Object.values(value).forEach((property, key, map) => {
      if (typeof property === 'object' && !property[1]) {
        let target = g.nodes.filter(x => {
          if (x.name === property[0].to) {
            return x;
          }
        });

        g.links.push({
          source: index,
          target: g.nodes.indexOf(target[0]),
          type: property[0].relation_type,
          linkShape: 0,
          marked: 0,
          hoover: 0
        });
      }
    });
  });

  //add factor for duplicate source and target
  g.links.forEach((value, key, map) => {
    if (value.linkShape !== 0) return;

    let a = g.links.filter(l => {
      return value.source === l.source && l.target === value.target;
    });
    let incr = 0;
    a.forEach((value, key, map) => {
      value.linkShape = incr;
      incr += 150;
    });
  });

  newState.displayGraph = g;
  return newState;
}
