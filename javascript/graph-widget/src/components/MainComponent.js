/**
 * The main component for the graph widget.
 */

import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Grid, Menu, Segment } from 'semantic-ui-react';

import { setActiveMenuItem } from '../reducers/uiState/menu';
import { getMetaGraph } from '../reducers/neo4j';
import AccessRules from './AccessRulesComponent';
import GraphView from './GraphViewComponent';
import Help from './HelpComponent';

class Main extends Component {
  displayName = 'Main';

  static propTypes = {
    actions: PropTypes.object.isRequired,
    menu: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props);
    this.menuItems = ['access rules', 'help'];
  }

  onItemClick = (e, { name }) => this.props.actions.setActiveMenuItem(name);

  getMenuComponent(name) {
    switch (name) {
      case 'access rules':
        return <AccessRules />;
      default:
        return <Help />;
    }
  }

  componentDidMount() {
    this.props.actions.getMetaGraph();
  }

  render() {
    const activeItem = this.props.menu.get('activeItem');
    return (
      <Grid>
        <Grid.Column width={4}>
          <Menu fluid vertical tabular>
            {this.menuItems.map((item, index) => {
              return (
                <Menu.Item
                  key={index}
                  name={item}
                  active={activeItem === item}
                  onClick={this.onItemClick}
                />
              );
            })}
          </Menu>
        </Grid.Column>

        <Grid.Column stretched width={12}>
          <Segment>
            {this.getMenuComponent(activeItem)}
          </Segment>
        </Grid.Column>

        <Grid.Row centered columns={12}>
          <Grid.Column width={4} />
          <Grid.Column width={12}> <GraphView /></Grid.Column>

        </Grid.Row>
      </Grid>
    );
  }
}

export default connect(
  state => ({
    menu: state.uiState.menu
  }),
  dispatch => ({
    actions: bindActionCreators(
      Object.assign(
        {},
        {
          setActiveMenuItem,
          getMetaGraph
        }
      ),
      dispatch
    )
  })
)(Main);
