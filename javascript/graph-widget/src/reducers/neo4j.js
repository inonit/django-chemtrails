import { Map, fromJS } from 'immutable'

export const FETCH_META_GRAPH = 'FETCH_META_GRAPH';
export const FETCHED_META_GRAPH = 'FETCHED_META_GRAPH';

const initialState = Map({
  metaGraph: Map({})
});
export default function reducer(state = initialState, action) {
  switch (action.type) {
    case FETCHED_META_GRAPH:
      return state.set('metaGraph', fromJS(action.payload));
    default:
      return state;
  }
}

export function getMetaGraph() {
  return {type: FETCH_META_GRAPH}
}
