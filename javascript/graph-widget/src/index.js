import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';

import configureStore from './store'
import App from './App';
import './index.css';


const run = () => {
  const __INITIAL_STATE__ = window.__INITIAL_STATE__ || {};
  const store = configureStore(__INITIAL_STATE__);

  ReactDOM.render(
    <Provider store={store}>
      <App/>
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
