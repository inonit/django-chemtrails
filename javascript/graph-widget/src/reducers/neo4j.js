import { Map, fromJS } from 'immutable';

export const FETCH_META_GRAPH = 'FETCH_META_GRAPH';
export const FETCHED_META_GRAPH = 'FETCHED_META_GRAPH';

const initialState = Map({
  metaGraph: Map({}),
  displayGraph: {
    nodes: [],
    links: []
  }
});
export default function reducer(state = initialState, action) {
  switch (action.type) {
    case FETCHED_META_GRAPH:
      return fromJS(setGraphs(state, action.payload));
    default:
      return state;
  }
}

export function getMetaGraph() {
  return { type: FETCH_META_GRAPH };
}

function setGraphs(oldState, payload) {
  let newState = oldState.toJS();
  newState.metaGraph = payload;
  let g = {
    nodes: [],
    links: []
  };
  newState.metaGraph.forEach((value, key, map) => {
    g.nodes.push({ name: value.label, label: value.label, id: value.id });
  });
  newState.metaGraph.forEach((value, key, map) => {
    Object.values(value).forEach((property, key, map) => {
      if (typeof property === 'object' && !property[1]) {
        let target = g.nodes.filter(x => {
          if (x.name === property[0].to) {
            return x;
          }
        });

        g.links.push({
          source: key,
          target: g.nodes.indexOf(target[0]),
          type: property[0].relation_type
        });
      }
    });
  });
  newState.displayGraph = g;
  console.log(newState);
  return newState;
}
