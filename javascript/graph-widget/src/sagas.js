/**
 * Application Sagas.
 */
import { take, put, call, fork } from 'redux-saga/effects';
import * as neo4j from './reducers/neo4j';
import * as accessRuleControls from './reducers/uiState/accessRuleControls';
import {
  fetchInitialMetaGraph,
  fetchNodeList,
  postGraphRule,
  fetchGraphRule
} from './webapi';

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
 * Post access rule
 */
export function* sagaPostGraphRule(data) {
  const payload = yield call(postGraphRule, data);
  yield put({ type: neo4j.POSTED_GRAPH_RULE, payload });
}
export function* watchSagaPostGraphRule(data) {
  while (true) {
    const { payload } = yield take(neo4j.POST_GRAPH_RULE);

    yield fork(sagaPostGraphRule, payload);
  }
}
/**
 * Get access rule
 */
export function* sagaGetGraphRule(data) {
  const payload = yield call(fetchGraphRule, data);
  yield put({ type: neo4j.FETCHED_GRAPH_RULE, payload });
}
export function* watchSagaGetGraphRule(data) {
  while (true) {
    const { payload } = yield take(neo4j.FETCH_GRAPH_RULE);

    yield fork(sagaGetGraphRule, payload);
  }
}
export default function* rootSaga() {
  yield [
    fork(watchGetInitialGraph),
    fork(watchGetAccessRuleControlNodes),
    fork(watchSagaPostGraphRule),
    fork(watchSagaGetGraphRule)
  ];
}
