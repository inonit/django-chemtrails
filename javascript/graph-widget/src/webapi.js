import 'axios'

/**
 * Fetch a list of nodes and their relation types
 */
export function fetchNodeList() {
  return axios.get('http://localhost:8000/admin/chemtrails_permissions/accessrule/nodelist/')
}
