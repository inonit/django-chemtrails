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
import { selectDisplayNode } from '../reducers/neo4j';

class AccessRules extends Component {
  displayName = 'Access Rules';

  constructor(props) {
    super(props);
  }

  onSourceNodeSelect = (e, { value }) => {
    this.props.actions.selectDisplayNode(value);
    this.props.actions.setSourceNode(value);
  };
  onTargetNodeSelect = (e, { value }) => {
    this.props.actions.selectDisplayNode(value);
    this.props.actions.setTargetNode(value);
  };
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

    const GRAPH = this.props.neo4j.toJS().displayGraph;

    let nodeTargets = [];
    let nodes = GRAPH.nodes.map((x, index) => {
      return { text: x.name, value: x.name, id: index };
    });
    let selectedSource = GRAPH.nodes.find(x => {
      return state.get('tempSourceNode') === x.name;
    });

    let relObjects = GRAPH.links.filter(x => {
      return GRAPH.nodes.indexOf(selectedSource) === x.source ||
        GRAPH.nodes.indexOf(selectedSource) === x.target;
    });
    let selectedRel = GRAPH.links.filter(x => {
      return state.get('tempRelation') === x.type &&
        GRAPH.nodes.indexOf(selectedSource) === x.source;
    });

    let rel = relObjects.map(x => {
      console.log(x);
      return { text: x.type, value: x.type };
    });
    let targetObj;
    //  console.log(nodes);
    // GRAPH.get('metaGraph').map(item => {
    //   nodes.push({ text: item.get('label'), value: item.get('label') });
    //   //relation from:
    //   if (item.toJS().label === state.get('tempSourceNode')) {
    //     item.forEach((value, key, map) => {
    //       if (typeof value === 'object' && key !== 'default_permissions') {
    //         rel.push({
    //           text: value.toJS()[0].relation_type,
    //           value: value.toJS()[0].relation_type
    //         });
    //       }
    //     });
    //   }
    //   //relations pointing to:
    //   item.forEach((value, key, map) => {
    //     if (typeof value === 'object' && key !== 'default_permissions') {
    //       value.map(item => {
    //         if (item.get('to') === state.get('tempSourceNode')) {
    //           rel.push({
    //             text: item.get('relation_type'),
    //             value: item.get('relation_type')
    //           });
    //         }
    //       });
    //     }
    //   });
    // });
    //
    //filter dups:
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
            disabled={!state.get('tempSourceNode')}
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
          setDirection,
          selectDisplayNode
        }
      ),
      dispatch
    )
  })
)(AccessRules);
