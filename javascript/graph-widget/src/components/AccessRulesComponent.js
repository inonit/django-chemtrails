import React, { Component } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { Form } from 'semantic-ui-react';
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

    let nodes = [];
    const GRAPH = this.props.neo4j;
    let rel = [];

    GRAPH.get('metaGraph').map(item => {
      nodes.push({ text: item.get('label'), value: item.get('label') });

      item.forEach((value, key, map) => {
        if (typeof value === 'object' && key !== 'default_permissions') {
          value.map(item => {
            if (item.get('to') === state.get('tempSourceNode')) {
              rel.push({
                text: item.get('relation_type'),
                value: item.get('relation_type')
              });
            }
          });
        }
      });
    });
    var arr = {};

    for (var i = 0, len = rel.length; i < len; i++)
      arr[rel[i]['text']] = rel[i];

    rel = new Array();
    for (var key in arr)
      rel.push(arr[key]);

    return (
      <Form>
        <Form.Group widths="equal">
          <Form.Select
            label="Source node"
            placeholder="Choose source node"
            defaultValue={state.get('tempSourceNode')}
            options={nodes}
            onChange={this.onSourceNodeSelect}
          />
          <Form.Select
            label="relations"
            placeholder="Choose a relation"
            options={rel}
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
            options={nodes}
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
    uiState: state.uiState,
    neo4j: state.neo4j
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
