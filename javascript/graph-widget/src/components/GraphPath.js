import React, { Component } from 'react';
import GraphPathD3 from './GraphPathD3';
import ReactDOM from 'react-dom';

class GraphPath extends Component {
  constructor(props) {
    super(props);
  }
  render() {
    return <div className={'bubble-chart-container '} width="1500" height="1200" />;
  }
  componentDidMount() {
    //GraphPathD3.create(this.getDOMNode(), this.getChartState());
    this.path = new GraphPathD3(this.getDOMNode(), this.getChartState());
  }

  componentDidUpdate() {
    this.path.update(this.getDOMNode(), this.getChartState());
  }

  getChartState() {
    return {
      data: this.props.data,
      nodes: this.props.nodes,
      links: this.props.links
    };
  }

  componentWillUnmount() {
    this.path.destroy(this.getDOMNode());
  }

  getDOMNode() {
    return ReactDOM.findDOMNode(this);
  }
}
export default GraphPath;
