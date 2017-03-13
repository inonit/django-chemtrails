import { combineReducers } from 'redux';
import { store as cyReducer } from 'cy-network-store';
import { default as neo4j } from './neo4j';
import { default as settings } from './settings';
import { default as uiState } from './uiState';

const rootReducer = combineReducers({
  ...cyReducer,
  neo4j,
  settings,
  uiState
});

export default rootReducer;
