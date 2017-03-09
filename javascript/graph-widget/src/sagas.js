/**
 * Application Sagas.
 */

import { take, put, call, fork, takeLatest } from 'redux-saga/effects'
import * as accessRuleControls from './reducers/uiState/accessRuleControls'
import { fetchNodeList } from './webapi'


/**
 * Fetches a list of nodes from the backend.
 */
export function* getAccessRuleControlNodes() {
  const payload = yield call(fetchNodeList);
  yield put({type: accessRuleControls.FETCHED_NODELIST, payload})
}
export function* watchGetAccessRuleControlNodes() {
  while (true) {
    yield take(accessRuleControls.FETCH_NODELIST);
    yield fork(getAccessRuleControlNodes)
  }
}

export default function* rootSaga() {
  yield [
    fork(watchGetAccessRuleControlNodes)
  ]
}
