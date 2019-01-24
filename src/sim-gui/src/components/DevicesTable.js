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
            <th>ID</th>
            <th>IP</th>
            <th>Port</th>
            <th>CRITICAL CPU</th>
            <th>CRITICAL MEM</th>
            <th>AVG CPU Usage</th>
            <th>AVG MEM Usage</th>
            <th>AVG #MYAPP</th>
            <th>DOWN PROB</th>
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
                <td>{(dev.CRITICAL_CPU_PERCENTAGE * 100).toFixed(2)} %</td>
                <td>{(dev.CRITICAL_MEM_PERCENTAGE * 100).toFixed(2)} %</td>
                <td>{(dev.AVERAGE_CPU_USED).toFixed(2)+"/"+dev.totalCPU}</td>
                <td>{(dev.AVERAGE_MEM_USED).toFixed(2)+"/"+dev.totalMEM}</td>
                <td>{(dev.AVERAGE_MYAPP_COUNT.toFixed(2))}</td>
                <td>{(dev.DEVICE_DOWN_PROB_chaos * 100).toFixed(2)} %</td>
              </tr>
            ))
          }
        </tbody>
      </Table>
    );
  }
}