/**
 * Component for displaying the graph.
 */

import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import * as d3 from 'd3';
import ReactFauxDOM from 'react-faux-dom';
import Graph from './Graph';

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
    const NEO = this.props.neo4j;
    const PATH = STATE.get('path');
    var dataset = [5, 10, 15, 20, 25];
    var displayGraph = NEO.get('displayGraph');
    var graph = {
      nodes: [
        { name: 'Peter', label: 'Person', id: 1 },
        { name: 'Michael', label: 'Person', id: 2 },
        { name: 'Neo4j', label: 'Database', id: 3 }
      ],
      links: [
        { source: 0, target: 1, type: 'KNOWS', since: 2010 },
        { source: 0, target: 1, type: 'FOUNDED' },
        { source: 1, target: 2, type: 'WORKS_ON' }
      ]
    };
    const someDiv = new ReactFauxDOM.Element('div');
    someDiv.setAttribute('height', 960);
    someDiv.setAttribute('width', 500);
    // console.log(STATE.toJS());
    console.log(NEO.toJS().displayGraph.links[0]);
    console.log(graph.links[0]);
    //d3
    //  .select(someDiv)
    //  .selectAll('p')
    //  .data(dataset)
    //  .enter()
    //  .append('p')
    //  .text('hei');

    ///

    ///
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
          : 'hade'}

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
const nodeCount = 10;
const nodes = [];
for (let i = 0; i < nodeCount; i++) {
  nodes.push({
    r: Math.random() * 5 + 2,
    x: 0,
    y: 0
  });
}
const links = [];
for (let i = 0; i < nodeCount; i++) {
  let target = 0;
  do {
    target = Math.floor(Math.random() * nodeCount);
  } while (target == i);
  links.push({
    source: i,
    target
  });
}

export default connect(
  state => ({
    uiState: state.uiState,
    neo4j: state.neo4j
  }),
  dispatch => ({})
)(GraphView);
