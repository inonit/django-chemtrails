import { combineReducers } from 'redux'
import { store as cyReducer } from 'cy-network-store'
import { default as settings } from './settings'
import { default as uiState } from './uiState'

const rootReducer = combineReducers({
  ...cyReducer,
  settings,
  uiState
});

export default rootReducer;
