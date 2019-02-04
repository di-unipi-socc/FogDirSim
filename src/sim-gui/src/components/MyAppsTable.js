import React from 'react';
import { Table } from 'reactstrap';
import { URL } from "../costants"
import MyAppDevice from "./MyAppDevice"
import {PieChart} from 'react-easy-chart';
import Quadretti from "./Quadretti"

let alert_to_color = {
  "APP_HEALTH": "#CD533B",
  "DEVICE_REACHABILITY": "#33753e",
  "MYAPP_CPU_CONSUMING": "#E3B505",
  "MYAPP_MEM_CONSUMING": "#4392F1"
}

export default class MyAppsTable extends React.Component {
  constructor(props){
    super(props)
    this.state = {myapps: [], myappOnDevice: []}
  }

  getData = () => {
    fetch(URL+"/result/myapps")
      .then(res => res.json())
      .then(res => this.setState({myapps: res}))
    setTimeout(this.getData, 1000)
  }

  componentWillMount(){
    this.getData()
  }

  render() {
    return (
      <Table striped>
        <thead>
          <tr>
            <th scope="row">#</th>
            <th>MyApp ID</th>
            <th>Name</th>
            <th>Up Prob.</th>
            <th>Down Prob.</th>
            <th>Installed Probability</th>
            <th>Alerts</th>
          </tr>
        </thead>
        <tbody>
          {
            this.state.myapps.map((myapp, i) => {
              let pie_data = []
              let total = 100
              for (let k in myapp.ALERT_PERCENTAGE){
                total -= myapp.ALERT_PERCENTAGE[k]
                pie_data.push({key: k, value: myapp.ALERT_PERCENTAGE[k]*100, color: alert_to_color[k]})
              }
              pie_data.push({key: "no_alert", value: total, color: "green"})
              return <tr key={myapp.myappId}>
              <td>{i}</td>
              <td>{myapp.myappId}</td>
              <td>{myapp.name}</td>
              <td>{(myapp.UP_PERCENTAGE * 100).toFixed(2)} %</td>
              <td>{(100 - (myapp.UP_PERCENTAGE * 100)).toFixed(2)} %</td>
              <td>{Object.keys(myapp.ON_DEVICE_PERCENTAGE)
                        .map(k => <MyAppDevice key={k} deviceId={k} time={myapp.ON_DEVICE_PERCENTAGE[k] * 100} startTime={myapp.ON_DEVICE_START_TIME[k]*100}/>)}
                </td>
              <td>
                <table className="quadretto">
                <tbody><tr>
                  <td>
                    {pie_data.reduce((p, v) => p+v.value, 0) == 0 ? "No alerts" :
                    <PieChart
                      key={myapp.myappId}
                      id={myapp.myappId}
                      size={100}
                      innerHoleSize={0}
                      data={pie_data}
                    />
                  }
                  </td>
                  <td>
                    <Quadretti data={pie_data.map(val => { return {color: val.color, val: val.value, name: val.key}} )} />
                  </td>
                  </tr>
                </tbody>
                </table>
              </td>
            </tr>
            })
          }
        </tbody>
      </Table>
    );
  }
}