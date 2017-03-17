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
    this.force = d3
      .forceSimulation(this.state.nodes)
      .force(
        'collide',
        d3
          .forceCollide(function(d) {
            return d.r + 8;
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
          .links(this.state.links)
      )
      .force('x', d3.forceX(this.props.width / 2))
      .force('y', d3.forceY(this.props.height / 2));

    this.force.on('tick', () => this.setState({
      links: this.state.links,
      nodes: this.state.nodes
    }));
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
    return (
      <svg width={this.props.width} height={this.props.height}>

        {this.state.links.map((link, index) => (
          <line
            x1={link.source.x}
            y1={link.source.y}
            x2={link.target.x}
            y2={link.target.y}
            key={`line-${index}`}
            stroke="black"
          />
        ))}
        {this.state.links.map((link, index) => (
          <text
            key={`text-${index}`}
            x={link.source.x}
            y={link.target.y}
            fontFamily="sans-serif"
            textAnchor="middle"
            fontSize="20px"
            fill="black">
            {link.type}
          </text>
        ))}
        {this.state.nodes.map((node, index) => (
          <circle r="20" cx={node.x} cy={node.y} fill="red" key={index} />
        ))}
        {this.state.nodes.map((node, index) => (
          <text
            key={`text-${index}`}
            x={node.x}
            y={node.y}
            fontFamily="sans-serif"
            fontSize="12px"
            fill="black">
            {node.name}

          </text>
        ))}

      </svg>
    );
  }
}
function linkPosition(source, target) {
  if (source === 'undefined') return 0;
  return source > target ? source - 40 : source + 40;
}
Graph.defaultProps = {
  width: 900,
  height: 600,
  linkDistance: 300,
  forceStrength: -20
};
export default Graph;
