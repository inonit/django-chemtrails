import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import * as d3 from 'd3';
import Faux from 'react-faux-dom';
import {
  selectDisplayNode,
  selectDisplayLink,
  toggleLinkToSelectedGraph,
  toggleNodeToSelectedGraph,
  getNewRule
} from '../reducers/neo4j';

class GraphComponent extends Component {
  constructor(props) {
    super(props);
    this.state = {
      nodes: props.graph.toJS().nodes,
      links: props.graph.toJS().links
    };
    console.log(props);
    console.log(this.state);
    this.force = d3
      .forceSimulation()
      .force(
        'collide',
        d3
          .forceCollide(function(d) {
            return 100;
          })
          .iterations(16)
      )
      .force('charge', d3.forceManyBody().strength(this.props.forceStrength))
      .force(
        'link',
        d3
          .forceLink()
          .id(function(d, i) {
            return i;
          })
          .distance(this.props.linkDistance)
      )
      .force('x', d3.forceX(this.props.width / 2))
      .force('y', d3.forceY(this.props.height / 2));

    this.force.on('tick', () => {
      this.node
        .attr('cx', d => {
          return d.x;
        })
        .attr('cy', d => {
          return d.y;
        })
        .attr('fill', d => {
          return d.marked ? 'blue' : 'red';
        });

      // nodeText
      //   .attr('x', d => {
      //     return d.x;
      //   })
      //   .attr('y', d => {
      //     return d.y;
      //   });
      //
      // path
      //   .attr('d', d => {
      //     var dx = d.target.x - d.source.x,
      //       dy = d.target.y - d.source.y,
      //       dr = Math.sqrt(dx * dx + dy * dy);
      //     return 'M' +
      //       d.source.x +
      //       ',' +
      //       d.source.y +
      //       'A' +
      //       (dr + d.linkShape) +
      //       ',' +
      //       (dr + d.linkShape) +
      //       ' 0 0,1 ' +
      //       d.target.x +
      //       ',' +
      //       d.target.y;
      //   })
      //   .attr('stroke', d => {
      //     return d.marked ? 'black' : 'red';
      //   });
      // pathshadow
      //   .attr('d', d => {
      //     var dx = d.target.x - d.source.x,
      //       dy = d.target.y - d.source.y,
      //       dr = Math.sqrt(dx * dx + dy * dy);
      //     return 'M' +
      //       d.source.x +
      //       ',' +
      //       d.source.y +
      //       'A' +
      //       (dr + d.linkShape) +
      //       ',' +
      //       (dr + d.linkShape) +
      //       ' 0 0,1 ' +
      //       d.target.x +
      //       ',' +
      //       d.target.y;
      //   })
      //   .attr('stroke', d => {
      //     return !d.hoover ? 'transparent' : 'yellow';
      //   });
      // this.setState({
      //   links: this.state.links,
      //   nodes: this.state.nodes
      // });
    });
  }

  componentDidMount() {}

  render() {
    var svg = d3.select(Faux.createElement('svg'));
    this.node = svg
      .append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(this.props.nodes)
      .enter()
      .append('circle')
      .attr('fill', d => {
        return d.marked ? 'blue' : 'red';
      })
      .attr('r', 40)
      .on('click', d => {
        //  console.log(d);
        d.marked = !d.marked ? 1 : 0;

        this.props.actions.selectDisplayNode(d.name);
        this.props.actions.toggleNodeToSelectedGraph(d);
        //if (!d3.event.active) this.force.alphaTarget(0.3).restart();
      })
      .call(
        d3
          .drag()
          .on('start', d => {
            if (!d3.event.active) this.force.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', d => {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
          })
          .on('end', d => {
            if (!d3.event.active) this.force.alphaTarget(0);
            d.x = d.fx;
            d.y = d.fy;
          })
      );
    this.node.append('title').text(function(d) {
      return d.name;
    });
    console.log(this.props);
    this.force.nodes(this.props.nodes);
    return svg.node().toReact();
  }
}

GraphComponent.defaultProps = {
  width: 1500,
  height: 1200,
  linkDistance: 300,
  forceStrength: -30
};
export default connect(
  state => ({
    neo4j: state.neo4j,
    graph: state.neo4j.get('displayGraph'),
    nodes: state.neo4j.get('displayGraph').toJS().nodes,
    links: state.neo4j.get('displayGraph').toJS().links
  }),
  dispatch => ({
    actions: bindActionCreators(
      Object.assign(
        {},
        {
          selectDisplayNode,
          selectDisplayLink,
          toggleLinkToSelectedGraph,
          toggleNodeToSelectedGraph,
          getNewRule
        }
      ),
      dispatch
    )
  })
)(GraphComponent);
