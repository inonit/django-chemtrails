import { Map, fromJS } from 'immutable';

export const FETCH_META_GRAPH = 'FETCH_META_GRAPH';
export const FETCHED_META_GRAPH = 'FETCHED_META_GRAPH';
export const MARK_DISPLAY_NODE = 'MARK_DISPLAY_NODE';
export const MARK_DISPLAY_LINK = 'MARK_DISPLAY_LINK';
export const TOGGLE_NODE_TO_SELECTED_GRAPH = 'ADD_NODE_TO_SELECTED_GRAPH';
export const TOGGLE_LINK_TO_SELECTED_GRAPH = 'ADD_LINK_TO_SELECTED_GRAPH';
export const POST_GRAPH_RULE = 'POST_GRAPH_RULE';
export const POSTED_GRAPH_RULE = 'POSTED_GRAPH_RULE';

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
  let newState = oldState.toJS();

  //look for node and index:
  let link = newState.selectedGraph.links.find(x => {
    return x.index === payload.index;
  });
  let i = newState.selectedGraph.links.indexOf(link);

  //add if not present and return:
  if (i === -1) {
    newState.selectedGraph.links.push(payload);
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
    if (x.source === payload.source.index && x.target === payload.target.index) {
      x.marked = !x.marked;
    }
  });
  return newState;
}

function markDisplayGraph(oldState, payload) {
  let newState = oldState.toJS();
  console.log(payload);
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
