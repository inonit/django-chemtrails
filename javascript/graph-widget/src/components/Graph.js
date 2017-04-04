import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import * as d3 from 'd3';
import {
  selectDisplayNode,
  selectDisplayLink,
  addLinkToSelectedGraph,
  addNodeToSelectedGraph,
  postNewRule
} from '../reducers/neo4j';

class Graph extends Component {
  constructor(props) {
    super(props);
    this.state = {
      nodes: props.nodes,
      links: props.links
    };
  }

  componentDidMount() {
    this.props.actions.postNewRule('hello');
    var svg = d3.select('svg').append('svg');
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
      node
        .attr('cx', d => {
          return d.x;
        })
        .attr('cy', d => {
          return d.y;
        })
        .attr('fill', d => {
          return d.marked ? 'blue' : 'red';
        });

      nodeText
        .attr('x', d => {
          return d.x;
        })
        .attr('y', d => {
          return d.y;
        });

      path
        .attr('d', d => {
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
        })
        .attr('stroke', d => {
          return d.marked ? 'black' : 'red';
        });
      pathshadow
        .attr('d', d => {
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
        })
        .attr('stroke', d => {
          return !d.hoover ? 'transparent' : 'yellow';
        });
      // this.setState({
      //   links: this.state.links,
      //   nodes: this.state.nodes
      // });
    });
    svg
      .append('svg:defs')
      .selectAll('marker')
      .data(['end']) // Different link/path types can be defined here
      .enter()
      .append('svg:marker') // This section adds in the arrows
      .attr('id', String)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 50)
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
      .attr('stroke', d => {
        return d.marked ? 'black' : 'red';
      })
      .attr('marker-end', 'url(#end)')
      .on('click', d => {
        console.log(d);
        d.marked = !d.marked ? 1 : 0;
        this.props.actions.addLinkToSelectedGraph(d);
        if (!d3.event.active) this.force.alphaTarget(0.3).restart();
      });
    var pathshadow = svg
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
      .attr('stroke', 'blue')
      .attr('stroke-width', '5')
      .on('click', d => {
        console.log(d);
        d.marked = !d.marked ? 1 : 0;
        //this.props.actions.addLinkToSelectedGraph(d);
        this.props.actions.selectDisplayLink(d);

        if (!d3.event.active) this.force.alphaTarget(0.3).restart();
      })
      .on('mouseenter', d => {
        d.hoover = 1;

        if (!d3.event.active) this.force.alphaTarget(0).restart();
      })
      .on('mouseleave', d => {
        d.hoover = 0;

        if (!d3.event.active) this.force.alphaTarget(0).restart();
      });
    let node = svg
      .append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(this.state.nodes)
      .enter()
      .append('circle')
      .attr('fill', d => {
        return d.marked ? 'blue' : 'red';
      })
      .attr('r', 40)
      .on('click', d => {
        //  console.log(d);
        d.marked = !d.marked ? 1 : 0;

        path
          .select(f => {
            if (f.source === d) {
              console.log(f);
              f.marked = !f.marked ? 1 : 0;
              this.props.actions.selectDisplayLink(f);
            }
          })
          .attr('fill', 'green');

        this.props.actions.selectDisplayNode(d.name);
        //this.props.actions.addNodeToSelectedGraph(d);
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
      .attr('text-anchor', 'middle')
      .style('font-size', '10px');

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
      .style('font-size', '8px')
      .attr('text-anchor', 'start')
      .style('fill', '#000')
      .append('textPath')
      .attr('xlink:href', function(d, i) {
        return '#linkId_' + i;
      })
      .attr('startOffset', '50%')
      .text(function(d) {
        return d.type;
      })
      .attr('refX', 60)
      .attr('refY', -1.5);

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

Graph.defaultProps = {
  width: 1500,
  height: 1200,
  linkDistance: 300,
  forceStrength: -30
};
export default connect(
  state => ({
    neo4j: state.neo4j
  }),
  dispatch => ({
    actions: bindActionCreators(
      Object.assign(
        {},
        {
          selectDisplayNode,
          selectDisplayLink,
          addLinkToSelectedGraph,
          addNodeToSelectedGraph,
          postNewRule
        }
      ),
      dispatch
    )
  })
)(Graph);
