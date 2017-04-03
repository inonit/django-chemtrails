/**
 * Component for displaying the graph.
 */

import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import * as d3 from 'd3';
import { Menu, Segment } from 'semantic-ui-react';
import { setActiveGraphItem } from '../reducers/uiState/menu';

import Graph from './Graph';
import GraphPath from './GraphPath';

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
    this.menuItems = ['graph', 'graphPath'];
  }
  onItemClick = (e, { name }) => this.props.actions.setActiveGraphItem(name);

  getMenuComponent(name) {
    const STATE = this.props.uiState.accessRuleControls;
    const NEO = this.props.neo4j;
    const PATH = STATE.get('path');

    switch (name) {
      case 'graph':
        return (
          <Graph
            key={NEO.toJS().displayGraph.nodes.length + PATH.length}
            nodes={NEO.toJS().displayGraph.nodes}
            links={NEO.toJS().displayGraph.links}
          />
        );
      default:
        return (
          <div>
            {PATH.map((value, index) => {
              return mapPath(value, index);
            })}
            <GraphPath
              data="hest"
              nodes={NEO.toJS().displayGraph.nodes}
              links={NEO.toJS().displayGraph.links}
            />
          </div>
        );
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
  // render() {
  //   const STATE = this.props.uiState.accessRuleControls;
  //   const NEO = this.props.neo4j;
  //   const PATH = STATE.get('path');
  //
  //   return (
  //     <div>
  //       <h1>Here be graph!</h1>
  //       {PATH.map((value, index) => {
  //         return mapPath(value, index);
  //       })}
  //       {NEO !== []
  //         ? <Graph
  //             key={NEO.toJS().displayGraph.nodes.length + PATH.length}
  //             nodes={NEO.toJS().displayGraph.nodes}
  //             links={NEO.toJS().displayGraph.links}
  //           />
  //         : ''}
  //     </div>
  //   );
  // }
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
