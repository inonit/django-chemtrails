import { combineReducers } from 'redux'
import { default as menu } from './menu'
import { default as accessRuleControls } from './accessRuleControls'

export default combineReducers({
  menu,
  accessRuleControls
});
