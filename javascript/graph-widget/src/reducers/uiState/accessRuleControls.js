import { Map, List, fromJS } from 'immutable';

export const FETCH_NODELIST = 'FETCH_NODELIST';
export const FETCHED_NODELIST = 'FETCHED_NODELIST';
const SET_SOURCE_NODE = 'SET_SOURCE_NODE';
const SET_TARGET_NODE = 'SET_TARGET_NODE';
const SET_RELATION = 'SET_RELATION';
const ADD_PATH = 'ADD_PATH';
const SET_DIRECTION = 'SET_DIRECTION';

const INTIAL_STATE = Map({
  path: [],
  nodeRelations: Map({}),
  tempSourceNode: undefined,
  tempRelation: undefined,
  tempTargetNode: undefined,
  tempDirection: undefined
});
export default function reducer(state = INTIAL_STATE, action) {
  switch (action.type) {
    case FETCHED_NODELIST:
      return state.set('nodeRelations', fromJS(action.payload));
    case SET_SOURCE_NODE:
      return state.set('tempSourceNode', fromJS(action.payload));
    case SET_TARGET_NODE:
      return state.set('tempTargetNode', fromJS(action.payload));
    case SET_RELATION:
      return state.set('tempRelation', fromJS(action.payload));
    case ADD_PATH:
      return fromJS(addPathClearTemp(state));
    case SET_DIRECTION:
      return state.set('tempDirection', fromJS(action.payload));
    default:
      return state;
  }
}

export function fetchNodeList() {
  return { type: FETCH_NODELIST };
}

export function setSourceNode(name) {
  return {
    type: SET_SOURCE_NODE,
    payload: name
  };
}

export function setTargetNode(name) {
  return {
    type: SET_TARGET_NODE,
    payload: name
  };
}
export function setRelation(name) {
  return {
    type: SET_RELATION,
    payload: name
  };
}
export function addPath() {
  return {
    type: ADD_PATH
  };
}
export function setDirection(name) {
  return {
    type: SET_DIRECTION,
    payload: name
  };
}

function addPathClearTemp(state) {
  const OLD_STATE = state.toJS();
  const NEW_STATE = OLD_STATE;
  NEW_STATE.path.push({
    sourceNode: OLD_STATE.tempSourceNode,
    relation: OLD_STATE.tempRelation,
    targetNode: OLD_STATE.targetNode,
    direction: OLD_STATE.tempDirection
  });
  NEW_STATE.tempTargetNode = undefined;
  NEW_STATE.tempSourceNode = undefined;
  NEW_STATE.tempRelation = undefined;
  NEW_STATE.tempDirection = undefined;

  return NEW_STATE;
}
