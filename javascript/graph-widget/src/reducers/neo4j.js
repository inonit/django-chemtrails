import { Map, fromJS } from 'immutable'

export const FETCH_INITIAL_GRAPH = 'FETCH_INITIAL_GRAPH';
export const FETCHED_INITIAL_GRAPH = 'FETCHED_INITIAL_GRAPH';

const initialState = Map({
  initialGraph: Map({})
});
export default function reducer(state = initialState, action) {
  switch (action.type) {
    case FETCHED_INITIAL_GRAPH:
      return state.set('initialGraph', fromJS(action.payload));
    default:
      return state;
  }
}

export function getInitialGraph() {
  return {type: FETCH_INITIAL_GRAPH}
}
