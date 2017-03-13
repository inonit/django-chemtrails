/**
 * Component for constructing CYPHER queries.
 */

import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';

class QueryBuilder extends Component {
  displayName = 'QueryBuilder';

  static propTypes = {};

  render() {
    return (
      <div>
        Hallo
      </div>
    );
  }
}

export default connect(state => ({}), dispatch => ({}))(QueryBuilder);
