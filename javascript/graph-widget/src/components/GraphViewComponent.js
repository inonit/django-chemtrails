/**
 * Component for displaying the graph.
 */

import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'

// import CyViewer from 'cy-viewer'


class GraphView extends Component {

  displayName = 'GraphView';

  static propTypes = {
    tag: PropTypes.string.isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.style = {
      width: '100%',
      height: '600px'
    }
  }

  render() {
    return (
      <div>
        <h1>Here be graph!</h1>
      </div>
    )
  }
}

export default connect(
  state => ({}),
  dispatch => ({})
)(GraphView)
