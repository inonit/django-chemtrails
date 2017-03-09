/**
 * Setup initial redux state.
 */

import { createStore, applyMiddleware, compose } from 'redux'
import createSagaMiddleware from 'redux-saga'
import rootReducer from './reducers'
import rootSaga from './sagas'

const reducer = compose()(rootReducer);
const sagaMiddleware = createSagaMiddleware();

const createConfigureStore = compose(
  applyMiddleware(sagaMiddleware),

  // Support Chrome "redux-devtools-extension"
  process.env.NODE_ENV !== 'production' && window.devToolsExtension ?
      window.devToolsExtension() : f => f
)(createStore);

export default function configureStore(initialState) {
  const store = createConfigureStore(reducer, initialState);
  sagaMiddleware.run(rootSaga);
  if (module.hot) {
    module.hot.accept('./reducers', () => {
      const nextReducer = require('./reducers');
      store.replaceReducer(nextReducer);
    });
  }
  return store;
}
