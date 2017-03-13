import { Map, fromJS } from 'immutable'

const initialState = Map({
  isConnected: false,
  driver: undefined
});
export default function reducer(state = initialState, action) {
  return state;
}
