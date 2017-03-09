import { Map, List, fromJS } from 'immutable'

export const FETCH_NODELIST = 'FETCH_NODELIST';
export const FETCHED_NODELIST = 'FETCHED_NODELIST';

const initialState = Map({
  nodeRelations: Map({})
});
export default function reducer(state = initialState, action) {
  switch (action.type) {
    case FETCHED_NODELIST:
      return state.set('nodeRelations', fromJS(action.payload));
    default:
      return state
  }
}


export function fetchNodeList() {
  return {type: FETCH_NODELIST}
}
