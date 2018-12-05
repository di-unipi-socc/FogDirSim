import React from 'react';
import { Table } from 'reactstrap';
import { URL } from "../costants"
import MyAppDevice from "./MyAppDevice"
export default class MyAppsTable extends React.Component {
  constructor(props){
    super(props)
    this.state = {myapps: [], myappOnDevice: []}
  }

  componentWillMount(){
    fetch(URL+"/result/myapps")
      .then(res => res.json())
      .then(res => this.setState({myapps: res}))
      .catch(err => alert("MyAppsTable Fetch Error "+err))
    fetch(URL+"/result/myappsstartstopdevice")
      .then(res => res.json())
      .then(res => this.setState({myappOnDevice: res}))
      .catch(err => alert("MyAppsTable-ondevice Fetch Error "+err))
  }

  render() {
    return (
      <Table striped>
        <thead>
          <tr>
            <th>#</th>
            <th>MyApp ID</th>
            <th>Name</th>
            <th>Installed Time</th>
            <th>Uninstalled Time</th>
            <th>Distribution Over Device</th>
          </tr>
        </thead>
        <tbody>
          {
            this.state.myapps.map((myapp, i) => (
              <tr key={myapp.myappId}>
                <td scope="row">{i}</td>
                <td>{myapp.myappId}</td>
                <td>{myapp.name}</td>
                <td>{(myapp.INSTALLED_TIME_PERCENTAGE * 100).toFixed(2)} %</td>
                <td>{(myapp.UNINSTALLED_TIME_PERCENTAGE * 100).toFixed(2)} %</td>
                <td>{this.state.myappOnDevice.filter( v => v.myappId == myapp.myappId )
                        .sort((a, b) => a.deviceId > b.deviceId ? 1 : -1)
                        .map(val => <MyAppDevice key={val.deviceId} deviceId={val.deviceId} start={val.START_TIME_PERCENTAGE*100} 
                                    stop={val.STOP_TIME_PERCENTAGE*100} time={val.INSTALL_ON_DEVICE_PERCENTAGE * 100}/>)}
                </td>
              </tr>
            ))
          }
        </tbody>
      </Table>
    );
  }
}