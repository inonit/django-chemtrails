/**
 * The main component for the graph widget.
 */

import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { Grid, Menu, Segment } from 'semantic-ui-react'

import { setActiveMenuItem } from '../reducers/uiState/menu'

import GraphView from './GraphViewComponent'

class Main extends Component {

  displayName = 'Main';

  static propTypes = {
    actions: PropTypes.object.isRequired,
    menu: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props)
  }

  onItemClick = (e, { name }) => this.props.actions.setActiveMenuItem({ activeItem: name });

  render() {
    const activeItem = {...this.props};
    return (
      <Grid>
        <Grid.Column width={4}>
          <Menu fluid vertical tabular>
            <Menu.Item name='bio' active={activeItem === 'bio'} onClick={this.onItemClick}/>
            <Menu.Item name='pics' active={activeItem === 'pics'} onClick={this.onItemClick}/>
            <Menu.Item name='companies' active={activeItem === 'companies'} onClick={this.onItemClick}/>
            <Menu.Item name='links' active={activeItem === 'links'} onClick={this.onItemClick}/>
          </Menu>
        </Grid.Column>

        <Grid.Column stretched width={12}>
          <Segment>
            This is an stretched grid column. This segment will always match the tab height
          </Segment>
        </Grid.Column>

        <Grid.Row centered columns={12}>
          <div><h1>Here be graph</h1></div>
        </Grid.Row>
      </Grid>
    )
  }
}

export default connect(
  state => ({
    menu: state.uiState.menu
  }),
  dispatch => ({
    actions: bindActionCreators(Object.assign({}, { setActiveMenuItem }), dispatch)
  })
)(Main)
