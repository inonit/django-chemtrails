import React, { Component } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { toJS } from 'immutable';

import { Form, Label } from 'semantic-ui-react';
import {
  fetchNodeList,
  setSourceNode,
  setTargetNode,
  setRelation,
  addPath,
  setDirection
} from '../reducers/uiState/accessRuleControls';

class AccessRules extends Component {
  displayName = 'Access Rules';

  constructor(props) {
    super(props);
  }

  onSourceNodeSelect = (e, { value }) =>
    this.props.actions.setSourceNode(value);
  onTargetNodeSelect = (e, { value }) =>
    this.props.actions.setTargetNode(value);
  onRelationSelect = (e, { value }) => this.props.actions.setRelation(value);
  onPathAdd = (e, { value }) => {
    e.preventDefault();

    this.props.actions.addPath();
  };
  onSetDirection = (e, { value }) => this.props.actions.setDirection(value);

  componentDidMount() {
    this.props.actions.fetchNodeList();
  }

  render() {
    const state = this.props.uiState.accessRuleControls;

    let nodeOptions = [];
    state.get('nodeRelations').map((relations, key) => {
      nodeOptions.push({ text: key, value: key });
    });
    let relOptions = [];
    state.get('nodeRelations').map((relations, key) => {
      if (key === state.get('tempSourceNode')) {
        relations.map((key, value) => {
          relOptions.push({ text: key, value: key });
        });
      }
    });
    return (
      <Form>
        <Form.Group widths="equal">
          <Form.Select
            label="Source node"
            placeholder="Choose source node"
            defaultValue={state.get('tempSourceNode')}
            options={nodeOptions}
            onChange={this.onSourceNodeSelect}
          />
          <Form.Select
            label="relations"
            placeholder="Choose a relation"
            options={relOptions}
            onChange={this.onRelationSelect}
            disabled={!state.get('tempSourceNode')}
          />
          <Form.Select
            label="direction"
            placeholder="Choose a direction"
            options={[
              { text: 'to', value: 'to' },
              { text: 'from', value: 'from' }
            ]}
            onChange={this.onSetDirection}
            disabled={!state.get('tempRelation')}
          />
          <Form.Select
            label="Target node"
            placeholder="Choose target node"
            defaultValue={state.get('tempTargetNode')}
            options={nodeOptions}
            onChange={this.onTargetNodeSelect}
            disabled={!state.get('tempsourceNode')}
          />
          <Form.Button onClick={this.onPathAdd}>Add</Form.Button>
        </Form.Group>
      </Form>
    );
  }
}

export default connect(
  state => ({
    settings: state.settings,
    uiState: state.uiState
  }),
  dispatch => ({
    actions: bindActionCreators(
      Object.assign(
        {},
        {
          fetchNodeList,
          setSourceNode,
          setTargetNode,
          setRelation,
          addPath,
          setDirection
        }
      ),
      dispatch
    )
  })
)(AccessRules);
