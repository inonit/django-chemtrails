import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Button, Card, Feed, Dropdown } from 'semantic-ui-react';
import { postNewRule } from '../reducers/neo4j';

class GraphItem extends Component {
  displayName = 'GraphItem';

  constructor(props) {
    super(props);
    this.permissions = [];
  }

  onDropDownChange = (e, { value }) => {
    this.permissions = value;
  };
  onSaveClick = (e, { value }) => {
    e.preventDefault();
    let graph = this.props.graph.toJS().selectedGraph;
    let postData = {
      sourceNode: graph.nodes[0],
      targetNode: graph.nodes[graph.nodes.length - 1],
      permissions: this.permissions,
      relationTypes: graph.links.map(x => {
        return x.type;
      })
    };
    this.props.actions.postNewRule(postData);
  };

  render() {
    let graph = this.props.graph.toJS().selectedGraph;
    let dispGraph = this.props.graph.toJS().displayGraph;
    //console.log(graph.nodes);
    return (
      <div>
        <Button floated="right" onClick={this.onSaveClick}>Save Rule</Button>
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
                  </Card.Description>
                  <Feed>
                    <Feed.Event>
                      <Feed.Content>
                        {graph.links.map(link => {
                          if (
                            link.source ===
                            dispGraph.nodes.indexOf(
                              dispGraph.nodes.find(x => {
                                return x.label === node.label;
                              })
                            )
                          ) {
                            return <p key={link.type}>{link.type}</p>;
                          }
                        })}
                      </Feed.Content>
                    </Feed.Event>
                  </Feed>
                  <div hidden={i !== graph.nodes.length - 1 || i === 0}>
                    <Card.Meta>
                      Select the premissions this rule will be applied to
                    </Card.Meta>
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

export default connect(
  state => ({
    graph: state.neo4j
  }),
  dispatch => ({
    actions: bindActionCreators(
      Object.assign(
        {},
        {
          postNewRule
        }
      ),
      dispatch
    )
  })
)(GraphItem);
