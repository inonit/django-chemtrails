/**
 * Fetch the initial meta graph data to display in the graph
 * visualization.
 */
export function fetchInitialMetaGraph() {
  return fetch(
    '//localhost:8000/admin/chemtrails_permissions/accessrule/neo4j/meta-graph/',
    {
      // credentials: 'include' // Must be enabled in production builds..
    },
  ).then(response => {
    if (response.status >= 400) {
      throw new Error('Bad response from the server');
    }
    return response.json();
  });
}

/**
 * Fetch a list of nodes and their relation types
 */
export function fetchNodeList() {
  return fetch(
    '//localhost:8000/admin/chemtrails_permissions/accessrule/neo4j/nodelist/',
    {
      // credentials: 'include' // Must be enabled in production builds..
    },
  ).then(response => {
    if (response.status >= 400) {
      throw new Error('Bad response from the server');
    }
    return response.json();
  });
}
export function postGraphRule(data) {
  console.log(data);
  let f = formatPermissions(data.permissions, data.targetNode.app_label);
  let body = {
    ctype_source: data.sourceNode.app_label + '.' + data.sourceNode.model_name,
    ctype_target: data.targetNode.app_label + '.' + data.targetNode.model_name,
    permissions: f,
    relation_types: data.relationTypes,
  };
  console.log(JSON.stringify(body));
  return fetch(
    '//localhost:8000/admin/chemtrails_permissions/accessrule/neo4j/access-rules/',
    {
      // credentials: 'include' // Must be enabled in production builds..
      method: 'POST',
      headers: new Headers({'Content-Type': 'application/json'}),
      body: JSON.stringify(body),
    },
  ).then(response => {
    if (response.status >= 400) {
      console.log(response);
      throw new Error('Bad response from the server');
    }
    return response.json();
  });
}

function formatPermissions(perm, appLabel) {
  return perm.map(p => {
    return appLabel + '.' + p;
  });
}
