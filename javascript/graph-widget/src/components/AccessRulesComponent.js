import React, { Component } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

import { Form } from 'semantic-ui-react'
import { fetchNodeList, setSourceNode, setTargetNode } from '../reducers/uiState/accessRuleControls'

class AccessRules extends Component {

  displayName = 'Access Rules';

  constructor(props) {
    super(props)
  }

  onSourceNodeSelect = (e, { value }) => this.props.actions.setSourceNode(value);
  onTargetNodeSelect = (e, { value }) => this.props.actions.setTargetNode(value);

  componentDidMount() {
    this.props.actions.fetchNodeList()
  }

  render() {
    const state = this.props.uiState.accessRuleControls;

    let nodeOptions = [];
    state.get('nodeRelations').map((relations, key) => {
      nodeOptions.push({text: key, value: key});
    });

    return (
      <Form>
        <Form.Group widths="equal">
          <Form.Select label="Source node" placeholder="Choose source node"
                       defaultValue={state.get('sourceNode')}
                       options={nodeOptions} onChange={this.onSourceNodeSelect}/>
          <Form.Select label="Target node" placeholder="Choose target node"
                       defaultValue={state.get('targetNode')}
                       options={nodeOptions} onChange={this.onTargetNodeSelect} disabled={!state.get('sourceNode')} />
        </Form.Group>
      </Form>
    );
  }
}

export default connect(
  state => ({
    uiState: state.uiState
  }),
  dispatch => ({
    actions: bindActionCreators(Object.assign({}, {
      fetchNodeList,
      setSourceNode,
      setTargetNode
    }), dispatch)
  })
)(AccessRules)
