import polyFetch from './polyFetch'



/**
 * Fetch the initial graph data to display in the graph
 * visualization.
 */
export function fetchInitialGraph() {
  return polyFetch.get({
    url: '//localhost:8000/admin/chemtrails_permissions/accessrule/neo4j-query/',
    data: {
      query: 'MATCH (n) RETURN n'
    }
  }).then((response) => {
    if (response.status >= 400) {
      throw new Error('Bad response from the server')
    }
    return response.json();
  });
  // return fetch('//localhost:8000/admin/chemtrails_permissions/accessrule/neo4j-query/', {
  //   // credentials: 'include' // Must be enabled in production builds..
  // }).then((response) => {
  //   if (response.status >= 400) {
  //     throw new Error('Bad response from the server')
  //   }
  //   return response.json();
  // })
}

/**
 * Fetch a list of nodes and their relation types
 */
export function fetchNodeList() {
  return fetch('//localhost:8000/admin/chemtrails_permissions/accessrule/nodelist/', {
    // credentials: 'include' // Must be enabled in production builds..
  }).then((response) => {
    if (response.status >= 400) {
      throw new Error('Bad response from the server')
    }
    return response.json();
  })
}
