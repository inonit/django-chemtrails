/**
 * Fetch the initial meta graph data to display in the graph
 * visualization.
 */
export function fetchInitialMetaGraph() {
  return fetch('//localhost:8000/admin/chemtrails_permissions/accessrule/neo4j/meta-graph/', {
    // credentials: 'include' // Must be enabled in production builds..
  }).then((response) => {
    if (response.status >= 400) {
      throw new Error('Bad response from the server')
    }
    return response.json();
  })
}

/**
 * Fetch a list of nodes and their relation types
 */
export function fetchNodeList() {
  return fetch('//localhost:8000/admin/chemtrails_permissions/accessrule/neo4j/nodelist/', {
    // credentials: 'include' // Must be enabled in production builds..
  }).then((response) => {
    if (response.status >= 400) {
      throw new Error('Bad response from the server')
    }
    return response.json();
  })
}
