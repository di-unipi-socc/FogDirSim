import React from 'react';
import { Table } from 'reactstrap';
import { URL } from "../costants"

export default class DevicesTable extends React.Component {
  constructor(props){
    super(props)
    this.state = {devices: []}
  }

  componentWillMount(){
    fetch(URL+"/result/devices")
      .then(res => res.json())
      .then(res => this.setState({devices: res}))
      .catch(err => alert("DeviceTable Fetch Error "+err))
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
            <th>CRITICAL CPU</th>
            <th>MEMORY UNDER HIGH PRESSURE</th>
          </tr>
        </thead>
        <tbody>
          {
            this.state.devices.map((dev, i) => (
              <tr key={dev.deviceId}>
                <td scope="row">{i}</td>
                <td>{dev.deviceId}</td>
                <td>{dev.ipAddress}</td>
                <td>{dev.port}</td>
                <td>{dev.FEW_CPU_PERCENTAGE * 100} %</td>
                <td>{dev.FEW_MEM_PERCENTAGE * 100} %</td>
              </tr>
            ))
          }
        </tbody>
      </Table>
    );
  }
}