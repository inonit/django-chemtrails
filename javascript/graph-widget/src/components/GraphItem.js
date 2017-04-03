import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { Button, Card, Image } from 'semantic-ui-react';

class GraphItem extends Component {
  displayName = 'GraphItem';

  static propTypes = {};

  render() {
    let graph = this.props.graph.toJS().selectedGraph;

    let last = graph.nodes[graph.nodes.length - 1];
    if (!last) {
      last = { item: {} };
    }

    return (
      <div>

        <Card.Group>

          <Card>
            <Card.Content>
              <Card.Header>
                {last.label}
              </Card.Header>
            </Card.Content>

          </Card>

        </Card.Group>
      </div>
    );
  }
}

export default connect(state => ({ graph: state.neo4j }), dispatch => ({}))(GraphItem);
