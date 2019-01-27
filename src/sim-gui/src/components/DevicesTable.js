import React from 'react';
import { Table } from 'reactstrap';
import { URL } from "../costants"
import AnimatedNumber from "animated-number-react"

export default class DevicesTable extends React.Component {
  constructor(props){
    super(props)
    this.state = {devices: []}
  }

  getData = () => {
    fetch(URL+"/result/devices")
      .then(res => res.json())
      .then(res => this.setState({devices: res}))
    setTimeout(this.getData, 3000)
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
            <th>MEAN COST</th>
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
                <td><AnimatedNumber key={dev.deviceId} value={Math.round(dev.CRITICAL_CPU_PERCENTAGE*100)/100} duration={1} formatValue={(val) =>( val * 100).toFixed(2) + " %"} /></td>
                <td><AnimatedNumber key={dev.deviceId} value={Math.round(dev.CRITICAL_MEM_PERCENTAGE*100)/100} duration={1} formatValue={(val) =>( val * 100).toFixed(2) + " %"} /></td>
                <td><AnimatedNumber key={dev.deviceId} value={Math.round((dev.AVERAGE_CPU_USED)*100)/100} duration={1} formatValue={(val) => val.toFixed(2)+"/"+dev.totalCPU}/></td>
                <td><AnimatedNumber key={dev.deviceId} value={Math.round((dev.AVERAGE_MEM_USED)*100)/100} duration={1} formatValue={(val) => val.toFixed(2)+"/"+dev.totalMEM}/></td>
                <td><AnimatedNumber key={dev.deviceId} value={Math.round((dev.AVERAGE_MYAPP_COUNT)*100)/100} duration={1} formatValue={(val) => val.toFixed(2)}/></td>
                <td><AnimatedNumber key={dev.deviceId} value={Math.round((dev.DEVICE_DOWN_PROB_chaos)*100)/100} duration={1} formatValue={(val) => (val*100).toFixed(2) +" %"}/></td>
                <td><AnimatedNumber key={dev.deviceId} value={Math.round((dev.DEVICE_ENERGY_CONSUMPTION)*100)/100} duration={1} formatValue={(val) => (val*100).toFixed(2)}/></td>
              </tr>
            ))
          }
        </tbody>
      </Table>
    );
  }
}