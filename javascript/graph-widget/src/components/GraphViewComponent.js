/**
 * Component for displaying the graph.
 */

import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Menu } from 'semantic-ui-react';
import { setActiveGraphItem } from '../reducers/uiState/menu';

import Graph from './Graph';
import GraphComponent from './GraphComponent';
import GraphPath from './GraphPath';

class GraphView extends Component {
  displayName = 'GraphView';

  constructor(props, context) {
    super(props, context);
    this.style = {
      width: '100%',
      height: '600px'
    };
    this.menuItems = ['graph', 'graphPath'];
  }
  onItemClick = (e, { name }) => this.props.actions.setActiveGraphItem(name);

  getMenuComponent(name) {
    const STATE = this.props.uiState.accessRuleControls;
    const NEO = this.props.neo4j;
    const PATH = STATE.get('path');
    //console.log(NEO.toJS().selectedGraph.nodes.length + PATH.length + 1);
    switch (name) {
      case 'graph':
        return (
          <Graph
            key={
              NEO.toJS().selectedGraph.nodes.length +
                NEO.toJS().displayGraph.nodes.length +
                PATH.length +
                1
            }
          />
        );
      default:
        return <GraphComponent />;
    }
  }
  render() {
    const activeItem = this.props.menu.get('activeGraphItem');

    return (
      <div>
        <Menu tabular>
          {this.menuItems.map((item, index) => {
            return (
              <Menu.Item
                key={index}
                name={item}
                onClick={this.onItemClick}
                active={activeItem === item}
              />
            );
          })}
        </Menu>

        {this.getMenuComponent(activeItem)}
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
    neo4j: state.neo4j,
    menu: state.uiState.menu
  }),
  dispatch => ({
    actions: bindActionCreators(
      Object.assign(
        {},
        {
          setActiveGraphItem
        }
      ),
      dispatch
    )
  })
)(GraphView);
