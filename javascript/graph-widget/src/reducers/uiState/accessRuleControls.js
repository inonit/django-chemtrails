import { Map, fromJS } from 'immutable'

export const FETCH_NODELIST = 'FETCH_NODELIST';
export const FETCHED_NODELIST = 'FETCHED_NODELIST';

const initialState = Map({});
export default function reducer(state = initialState, action) {
  switch (action.type) {
    case FETCHED_NODELIST:
      return state;
    default:
      return state
  }
}


export function fetchNodeList() {
  return {type: FETCH_NODELIST}
}
