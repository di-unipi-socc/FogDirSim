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
  }

  render() {
    return (
      <Table striped>
        <thead>
          <tr>
            <th>#</th>
            <th>MyApp ID</th>
            <th>Name</th>
            <th>Up Prob.</th>
            <th>Down Prob.</th>
            <th>Installed Probability</th>
          </tr>
        </thead>
        <tbody>
          {
            this.state.myapps.map((myapp, i) => {
              console.log(myapp.INSTALL_ON_DEVICE_PERCENTAGE)
              return <tr key={myapp.myappId}>
              <td scope="row">{i}</td>
              <td>{myapp.myappId}</td>
              <td>{myapp.name}</td>
              <td>{(myapp.UP_PERCENTAGE * 100).toFixed(2)} %</td>
              <td>{(100 - (myapp.UP_PERCENTAGE * 100)).toFixed(2)} %</td>
              <td>{Object.keys(myapp.ON_DEVICE_PERCENTAGE)
                        .map(k => <MyAppDevice key={k} deviceId={k} time={myapp.ON_DEVICE_PERCENTAGE[k] * 100}/>)}
                </td>
            </tr>
            })
          }
        </tbody>
      </Table>
    );
  }
}