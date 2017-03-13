/**
 * Component for displaying the graph.
 */

import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { toJS } from 'immutable';

// import CyViewer from 'cy-viewer'

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
    const PATH = STATE.get('path');

    return (
      <div>
        <h1>Here be graph!</h1>
        {PATH.map(value => {
          return mapPath(value);
        })}
      </div>
    );
  }
}
function mapPath(value) {
  return (
    <p key={value}>
      {value.toJS().sourceNode}
      {' '}
      {value.toJS().direction == 'to' ? '<-' : '->'}
      {' '}
      {value.toJS().relation}
      {value.toJS().direction}
    </p>
  );
}
export default connect(
  state => ({
    uiState: state.uiState
  }),
  dispatch => ({})
)(GraphView);
