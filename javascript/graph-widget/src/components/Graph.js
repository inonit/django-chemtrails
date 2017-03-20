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
      node
        .attr('cx', d => {
          return d.x;
        })
        .attr('cy', d => {
          return d.y;
        });

      nodeText
        .attr('x', d => {
          return d.x;
        })
        .attr('y', d => {
          return d.y;
        });

      path.attr('d', d => {
        //console.log(d.linkShape);
        var dx = d.target.x - d.source.x,
          dy = d.target.y - d.source.y,
          dr = Math.sqrt(dx * dx + dy * dy);
        return 'M' +
          d.source.x +
          ',' +
          d.source.y +
          'A' +
          (dr + d.linkShape) +
          ',' +
          (dr + d.linkShape) +
          ' 0 0,1 ' +
          d.target.x +
          ',' +
          d.target.y;
      });

      this.setState({
        links: this.state.links,
        nodes: this.state.nodes
      });
    });
    svg
      .append('svg:defs')
      .selectAll('marker')
      .data(['end']) // Different link/path types can be defined here
      .enter()
      .append('svg:marker') // This section adds in the arrows
      .attr('id', String)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 30)
      .attr('refY', -1.5)
      .attr('markerWidth', 10)
      .attr('markerHeight', 10)
      .attr('orient', 'auto')
      .append('svg:path')
      .attr('d', 'M0,-5L10,0L0,5');

    var path = svg
      .append('g')
      .selectAll('path')
      .data(this.state.links)
      .enter()
      .append('path')
      .attr('class', function(d) {
        return 'link ' + d.type;
      })
      .attr('id', function(d, i) {
        return 'linkId_' + i;
      })
      .attr('fill', 'none')
      .attr('stroke', 'black')
      .attr('marker-end', 'url(#end)');
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

    let nodeText = svg
      .append('g')
      .attr('class', 'nodeLabels')
      .selectAll('text')
      .data(this.state.nodes)
      .enter()
      .append('text')
      .text(d => {
        return d.name;
      })
      .attr('fill', 'black')
      .attr('text-anchor', 'middle');
    var linktext = svg
      .append('svg:g')
      .selectAll('g.linklabelholder')
      .data(this.state.links)
      .enter()
      .append('g')
      .attr('class', 'linklabelholder')
      .append('text')
      .text(d => {
        return d.type;
      })
      .attr('class', 'linklabel')
      .style('font-size', '13px')
      .attr('text-anchor', 'start')
      .style('fill', '#000')
      .append('textPath')
      .attr('xlink:href', function(d, i) {
        return '#linkId_' + i;
      })
      .attr('startOffset', '50%')
      .text(function(d) {
        return d.type;
      });

    this.force.nodes(this.state.nodes);
    this.force.force('link').links(this.state.links);
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
