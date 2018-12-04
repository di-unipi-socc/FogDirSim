import React from 'react';
import { Table } from 'reactstrap';

export default class Example extends React.Component {
  constructor(props){
    super(props)
    this.state = {device: []}
  }

  componentWillMount(){
    fetch()
      .then(res => res.json())
      .then(res => this.setState({device: res}))
  }

  render() {
    return (
      <Table>
        <thead>
          <tr>
            <th>#</th>
            <th>Device ID</th>
            <th>IP Address</th>
            <th>Port</th>
            <th>MEM_PRESSURE (%)</th>
            <th>CRITICAL_CPU (%)</th>
          </tr>
        </thead>
        <tbody>
          {
            this.stata.devices.map((dev, i) => (
              <tr>
                <td scope="row">{i}</td>
                <td></td>
              </tr>
            ))
          }
          <tr>
            <th scope="row">1</th>
            <td>Mark</td>
            <td>Otto</td>
            <td>@mdo</td>
          </tr>
          <tr>
            <th scope="row">2</th>
            <td>Jacob</td>
            <td>Thornton</td>
            <td>@fat</td>
          </tr>
          <tr>
            <th scope="row">3</th>
            <td>Larry</td>
            <td>the Bird</td>
            <td>@twitter</td>
          </tr>
        </tbody>
      </Table>
    );
  }
}