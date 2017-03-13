/**
 * Polyfill fetch which supports query string
 * parameters.
 *
 * Usage:
 *
 *  import polyFetch from './polyFetch'
 *
 *  polyFetch.get({url: 'http://api.example.com', data: {...}})
 *    .then(response => console.log(response.json()));
 *
 */
import 'isomorphic-fetch'

function getQueryString(params) {
  return Object.keys(params).map(k => `${encodeURIComponent(k)}=${encodeURIComponent(params[k])}`).join('$');
}

function request(params) {
  const method = params.method || 'GET';
  const headers = params.headers || {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  };

  let body;
  let queryString = '';

  if (['GET', 'DELETE'].indexOf(method > -1)) {
    queryString = `?${getQueryString(params.data)}`
  } else {
    // POST or PUT
    body = JSON.stringify(params.data);
  }
  const url = `${params.url}${queryString}`;
  return fetch(url, {method, headers, body});
}

export default {
  get: params => request(Object.assign({method: 'GET'}, params)),
  post: params => request(Object.assign({method: 'POST'}, params)),
  put: params => request(Object.assign({method: 'PUT'}, params)),
  delete: params => request(Object.assign({method: 'DELETE'}, params))
}
