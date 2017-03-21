/**
 * Component for displaying the graph.
 */

import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import * as d3 from 'd3';
import Graph from './Graph';

class GraphView extends Component {
  displayName = 'GraphView';

  static propTypes = {
    //tag: PropTypes.string.isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.style = {
      width: '100%',
      height: '600px'
    };
  }

  render() {
    const STATE = this.props.uiState.accessRuleControls;
    const NEO = this.props.neo4j;
    const PATH = STATE.get('path');

    return (
      <div>
        <h1>Here be graph!</h1>
        {PATH.map((value, index) => {
          return mapPath(value, index);
        })}
        {NEO !== []
          ? <Graph
              key={NEO.toJS().displayGraph.nodes.length}
              nodes={NEO.toJS().displayGraph.nodes}
              links={NEO.toJS().displayGraph.links}
            />
          : ''}
      </div>
    );
  }
}
function mapPath(value, index) {
  return (
    <p key={value}>
      {value.toJS().sourceNode}
      {' '}
      {value.toJS().direction === 'to' ? '<-' : '->'}
      {' '}
      {value.toJS().relation}
    </p>
  );
}

export default connect(
  state => ({
    uiState: state.uiState,
    neo4j: state.neo4j
  }),
  dispatch => ({})
)(GraphView);
