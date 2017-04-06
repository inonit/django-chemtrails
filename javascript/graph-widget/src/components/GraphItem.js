import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { Button, Card, Image, Feed, Dropdown } from 'semantic-ui-react';

class GraphItem extends Component {
  displayName = 'GraphItem';
  constructor(props) {
    super(props);
    this.permissions = [];
  }
  static propTypes = {};
  onDropDownChange = (e, { value }) => {
    this.permissions = value;
    console.log(this.permissions);
  };
  render() {
    let graph = this.props.graph.toJS().selectedGraph;

    return (
      <div>
        <Card.Group>
          {graph.nodes.map((node, i) => {
            return (
              <Card centered key={i}>
                <Card.Content>
                  <Card.Header>
                    {node.label}
                  </Card.Header>
                  <Card.Meta>{i === 0 ? 'Start' : ''}</Card.Meta>
                  <Card.Description>
                    {i === 0
                      ? '  This is the start position of your rule, normally the User Object'
                      : ''}
                    This is the start position of your rule, normally the User Object
                  </Card.Description>
                  <Feed>
                    <Feed.Event>
                      <Feed.Content>
                        {graph.links.map(link => {
                          if (link.source.item.id === node.id) {
                            return <p key={link.type}>{link.type}</p>;
                          }
                        })}
                      </Feed.Content>
                    </Feed.Event>
                  </Feed>
                  <div hidden={i != graph.nodes.length - 1 || i === 0}>
                    <Dropdown
                      placeholder="rights"
                      fluid
                      multiple
                      selection
                      options={node.model_permissions.map(perm => {
                        return { key: perm, value: perm, text: perm };
                      })}
                      onChange={this.onDropDownChange}
                    />
                  </div>
                </Card.Content>

              </Card>
            );
          })}
        </Card.Group>
      </div>
    );
  }
}

export default connect(state => ({ graph: state.neo4j }), dispatch => ({}))(GraphItem);
