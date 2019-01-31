import React from 'react';
import { Table } from 'reactstrap';
import { URL } from "../costants"
import CountUp from 'react-countup';

const update_time = 3

export default class DevicesTable extends React.Component {
  constructor(props){
    super(props)
    this.state = {devices: [], prev_devices: []}
  }

  getData = () => {
    fetch(URL+"/result/devices")
      .then(res => res.json())
      .then(res => this.setState({devices: res, prev_devices: this.state.devices.length === 0 ? res : this.state.devices}))
    setTimeout(this.getData, update_time*900)
  }

  componentWillMount(){
    this.getData()
  }

  render() {
    return (
      <Table>
        <thead>
          <tr>
            <th>#</th>
            <th scope="row">ID</th>
            <th>IP</th>
            <th>Port</th>
            <th>CRITICAL CPU</th>
            <th>CRITICAL MEM</th>
            <th>AVG CPU Usage</th>
            <th>AVG MEM Usage</th>
            <th>AVG #MYAPP</th>
            <th>DOWN PROB</th>
            <th>MEAN ENERGY</th>
          </tr>
        </thead>
        <tbody>
          {
            this.state.devices.map((dev, i) => (
              <tr key={dev.deviceId}>
                <td>{i}</td>
                <td>{dev.deviceId}</td>
                <td>{dev.ipAddress}</td>
                <td>{dev.port}</td>
                <td><CountUp key={dev.deviceId} end={dev.CRITICAL_CPU_PERCENTAGE*100}     start={this.state.prev_devices[i].CRITICAL_CPU_PERCENTAGE*100}   decimals={2}  suffix=" %"  /></td>
                <td><CountUp key={dev.deviceId} end={dev.CRITICAL_MEM_PERCENTAGE*100}     start={this.state.prev_devices[i].CRITICAL_MEM_PERCENTAGE*100}   decimals={2}  suffix=" %"   /></td>
                <td><CountUp key={dev.deviceId} end={(dev.AVERAGE_CPU_USED)}              start={this.state.prev_devices[i].AVERAGE_CPU_USED}              decimals={2}  suffix={"/"+dev.totalCPU.toFixed(2)}/></td>
                <td><CountUp key={dev.deviceId} end={(dev.AVERAGE_MEM_USED)}              start={this.state.prev_devices[i].AVERAGE_MEM_USED}              decimals={2}  suffix={"/"+dev.totalMEM.toFixed(2)}/></td>
                <td><CountUp key={dev.deviceId} end={(dev.AVERAGE_MYAPP_COUNT)}           start={this.state.prev_devices[i].AVERAGE_MYAPP_COUNT}           decimals={2} /></td>
                <td><CountUp key={dev.deviceId} end={(dev.DEVICE_DOWN_PROB_chaos*100)}    start={this.state.prev_devices[i].DEVICE_DOWN_PROB_chaos*100}    decimals={2}  suffix=" %" /></td>
                <td><CountUp key={dev.deviceId} end={(dev.DEVICE_ENERGY_CONSUMPTION * 0.72)}     start={this.state.prev_devices[i].DEVICE_ENERGY_CONSUMPTION * 0.72}     decimals={2}  suffix=" kWh/month" /></td>
              </tr>
            ))
          }
        </tbody>
      </Table>
    );
  }
}