import { Map, fromJS } from 'immutable';

const initialState = Map({
  baseUrl: '',
  neo4jUrl: ''
});

export default function reducer(state = initialState, action) {
  return state;
}
