/**
 * Application Sagas.
 */
import { take, put, select, call, fork } from 'redux-saga/effects'
import * as neo4j from './reducers/neo4j'
import * as accessRuleControls from './reducers/uiState/accessRuleControls'
import { fetchInitialMetaGraph, fetchNodeList } from './webapi'


/**
 * Fetches the initial graph data for the visualization
 */
export function* getInitialGraph() {
  const payload = yield call(fetchInitialMetaGraph);
  yield put({type: neo4j.FETCHED_META_GRAPH, payload})
}
export function* watchGetInitialGraph() {
  while (true) {
    yield take(neo4j.FETCH_META_GRAPH);
    yield fork(getInitialGraph);
  }
}

/**
 * Fetches a list of nodes from the backend.
 */
export function* getAccessRuleControlNodes() {
  const payload = yield call(fetchNodeList);
  yield put({type: accessRuleControls.FETCHED_NODELIST, payload});
}
export function* watchGetAccessRuleControlNodes() {
  while (true) {
    yield take(accessRuleControls.FETCH_NODELIST);
    yield fork(getAccessRuleControlNodes);
  }
}

export default function* rootSaga() {
  yield [
    fork(watchGetInitialGraph),
    fork(watchGetAccessRuleControlNodes)
  ]
}
