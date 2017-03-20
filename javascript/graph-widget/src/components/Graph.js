import React, { Component, PropTypes } from 'react';
import * as d3 from 'd3';

class Graph extends Component {
  constructor(props) {
    super(props);
    this.state = {
      nodes: props.nodes,
      links: props.links
    };
  }

  componentDidMount() {
    var svg = d3.select('svg').append('svg');
    this.force = d3
      .forceSimulation()
      .force(
        'collide',
        d3
          .forceCollide(function(d) {
            return 60;
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
      link
        .attr('x1', function(d) {
          return d.source.x;
        })
        .attr('y1', function(d) {
          return d.source.y;
        })
        .attr('x2', function(d) {
          return d.target.x;
        })
        .attr('y2', function(d) {
          return d.target.y;
        });
      node
        .attr('cx', function(d) {
          return d.x;
        })
        .attr('cy', function(d) {
          return d.y;
        });
      nodetext
        .attr('x', function(d) {
          return d.x;
        })
        .attr('y', function(d) {
          return d.y;
        });
      this.setState({
        links: this.state.links,
        nodes: this.state.nodes
      });
    });
    let link = svg
      .append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(this.state.links)
      .enter()
      .append('line')
      .attr('stroke', 'black')
      .attr('marker-end', 'url(#arrowhead)');

    let node = svg
      .append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(this.state.nodes)
      .enter()
      .append('circle')
      .attr('fill', 'red')
      .attr('r', 20)
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
    node.append('title').text(function(d) {
      return d.name;
    });
    let nodetext = svg
      .append('g')
      .selectAll('text')
      .data(this.state.nodes)
      .enter()
      .append('text')
      .text(d => {
        return d.name;
      })
      .attr('fill', 'black')
      .attr('x', 3.5)
      .attr('y', 3.5)
      .attr('text-anchor', 'middle');
    this.force.nodes(this.state.nodes);
    this.force.force('link').links(this.state.links);
    // let node = d3.selectAll('circle');
    // node.call(
    //   d3
    //     .drag()
    //     .on('start', d => {})
    //     .on('drag', d => {
    //       console.log(d);
    //     })
    //     .on('end', d => {
    //       if (!d3.event.active) this.force.alphaTarget(0);
    //     })
    // );
    // console.log(node);
  }

  componentWillUnmount() {
    this.force.stop();
  }
  componentWillReceiveProps(nextProps) {}
  render() {
    return <svg width={this.props.width} height={this.props.height} />;
  }
}
function linkPosition(source, target) {
  if (source === 'undefined') return 0;
  return source > target ? source - 40 : source + 40;
}
Graph.defaultProps = {
  width: 1200,
  height: 600,
  linkDistance: 300,
  forceStrength: -20
};
export default Graph;
