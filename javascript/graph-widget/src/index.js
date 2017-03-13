import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { Map } from 'immutable'

import configureStore from './store'
import Main from './components/MainComponent'


const run = () => {
  const __INITIAL_STATE__ = window.__INITIAL_STATE__ || {
    settings: Map({
      baseUrl: 'http://localhost:8000',
      neo4jUrl: 'bolt://neo4j:neo4j@localhost:7687'
    })
  };
  const store = configureStore(__INITIAL_STATE__);

  ReactDOM.render(
    <Provider store={store}>
      <Main/>
    </Provider>,
    document.getElementById('root')
  );
};

Promise.all([
  new Promise((resolve) => {
    if (window.addEventListener) {
      window.addEventListener('DOMContentLoaded', resolve)
    } else {
      window.attachEvent('onload', resolve)
    }
  })
]).then(run);
