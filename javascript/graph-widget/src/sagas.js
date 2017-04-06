/**
 * Application Sagas.
 */
import { take, put, select, call, fork } from 'redux-saga/effects';
import * as neo4j from './reducers/neo4j';
import * as accessRuleControls from './reducers/uiState/accessRuleControls';
import { fetchInitialMetaGraph, fetchNodeList, postGraphRule } from './webapi';

/**
 * Fetches the initial graph data for the visualization
 */
export function* getInitialGraph() {
  const payload = yield call(fetchInitialMetaGraph);
  yield put({ type: neo4j.FETCHED_META_GRAPH, payload });
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
  yield put({ type: accessRuleControls.FETCHED_NODELIST, payload });
}
export function* watchGetAccessRuleControlNodes() {
  while (true) {
    yield take(accessRuleControls.FETCH_NODELIST);
    yield fork(getAccessRuleControlNodes);
  }
}

/**
 * Fetches a list of nodes from the backend.
 */
export function* sagaPostGraphRule(data) {
  console.log(data);
  const payload = yield call(postGraphRule, data);
  yield put({ type: neo4j.POSTED_GRAPH_RULE, payload });
}
export function* watchSagaPostGraphRule(data) {
  while (true) {
    const { payload } = yield take(neo4j.POST_GRAPH_RULE);
    console.log(payload);
    yield fork(sagaPostGraphRule, payload);
  }
}

export default function* rootSaga() {
  yield [
    fork(watchGetInitialGraph),
    fork(watchGetAccessRuleControlNodes),
    fork(watchSagaPostGraphRule)
  ];
}
