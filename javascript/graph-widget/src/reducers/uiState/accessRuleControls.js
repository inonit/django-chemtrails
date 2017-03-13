import { Map, List, fromJS } from 'immutable'

export const FETCH_NODELIST = 'FETCH_NODELIST';
export const FETCHED_NODELIST = 'FETCHED_NODELIST';
const SET_SOURCE_NODE = 'SET_SOURCE_NODE';
const SET_TARGET_NODE = 'SET_TARGET_NODE';

const initialState = Map({
  sourceNode: '',
  targetNode: '',
  nodeRelations: Map({})
});
export default function reducer(state = initialState, action) {
  switch (action.type) {
    case FETCHED_NODELIST:
      return state.set('nodeRelations', fromJS(action.payload));
    case SET_SOURCE_NODE:
      return state.set('sourceNode', fromJS(action.payload));
    case SET_TARGET_NODE:
      return state.set('targetNode', fromJS(action.payload));
    default:
      return state
  }
}


export function fetchNodeList() {
  return {type: FETCH_NODELIST}
}

export function setSourceNode(name) {
  return {
    type: SET_SOURCE_NODE,
    payload: name
  }
}

export function setTargetNode(name) {
  return {
    type: SET_TARGET_NODE,
    payload: name
  }
}
