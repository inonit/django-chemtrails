import * as d3 from 'd3';

class GraphPathD3 {
  constructor(el, props) {
    (this.width = 1500), (this.height = 1200), (this.linkDistance = 300), (this.forceStrength = -30);
    this.el = d3
      .select(el)
      .append('svg')
      .attr('class', 'graph-path')
      .attr('width', this.width)
      .attr('height', this.height);

    (this.nodes = []), (this.links = []);

    this.simulation = d3
      .forceSimulation()
      .force(
        'link',
        d3.forceLink().id(function(d) {
          return d.id;
        })
      )
      .force('charge', d3.forceManyBody())
      .force('center', d3.forceCenter(this.width / 2, this.height / 2));
    var svg = d3.select('.graph-path');
    //  var linkLayer = svg.append('g').attr('id', 'link-layer');
    this.nodeLayer = svg.append('g').attr('id', 'node-layer');

    this.update(el, props);
  }

  update(el, props) {
    const DATA = props.data;
    if (!DATA) return;

    this.nodes = props.nodes;

    var node = this.nodeLayer.selectAll('.node').data(this.nodes, function(d) {
      return d.id;
    });

    node
      .enter()
      .append('circle')
      .attr('class', function(d) {
        return 'node ' + d.id;
      })
      .attr('fill', d => {
        return d.marked ? 'blue' : 'red';
      })
      .attr('r', 40)
      .on('click', d => {
        console.log(d);
        d.marked = 1;
        if (!d3.event.active) this.simulation.alphaTarget(0.3).restart();
      })
      .call(
        d3
          .drag()
          .on('start', d => {
            if (!d3.event.active) this.simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', d => {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
          })
          .on('end', d => {
            if (!d3.event.active) this.simulation.alphaTarget(0);
            d.x = d.fx;
            d.y = d.fy;
          })
      );
    node.append('title').text(function(d) {
      return d.name;
    });

    node.exit().remove();

    this.simulation.nodes(this.nodes).on('tick', () => {
      this.nodeLayer
        .selectAll('.node')
        .attr('cx', function(d) {
          return d.x;
        })
        .attr('cy', function(d) {
          return d.y;
        });
    });
  }

  /** Any necessary cleanup */
  destroy(el) {}
}

export default GraphPathD3;
