import React from 'react';
import { URL } from "../costants"
import Number from "./Number"
import {PieChart, LineChart} from 'react-easy-chart';
import Quadretti from "./Quadretti"

let alert_to_color = {
    "APP_HEALTH": "#CD533B",
    "DEVICE_REACHABILITY": "#33753e",
    "MYAPP_CPU_CONSUMING": "#e2b404",
    "MYAPP_MEM_CONSUMING": "#4392F1"
}

export default class Certificate extends React.Component {
    constructor(props){
        super(props)
        this.state = {cost: 0, uptime: 1, prev_cost: 0, prev_uptime: 1, pie_data: [], uptime_history: [], energy_history: []}
    }

    getData = () => {
      fetch(URL+"/result/devices")
        .then(res => res.json())
        .then(res => res.reduce((prev, current) => (prev+current.DEVICE_ENERGY_CONSUMPTION), 0))
        .then(cost => this.setState({cost: cost, prev_cost: this.state.cost, energy_history: [...this.state.energy_history, {x: this.state.energy_history.length + 1, y: cost}]}))
      fetch(URL+"/result/myapps")
        .then(res => res.json())
        .then(res => {
            let uptime = res.reduce((prev, current) => (prev+current.UP_PERCENTAGE), 0) / res.length
            let average_alerts = {}
            res.forEach(myapp => {
                for(let key in myapp.ALERT_PERCENTAGE){
                    if (average_alerts[key] != null){
                        average_alerts[key] += myapp.ALERT_PERCENTAGE[key]
                    }else{
                        average_alerts[key] = myapp.ALERT_PERCENTAGE[key]
                    }
                }
            })

            let pie_data = []
            let total = 1
            for (let k in average_alerts){
                pie_data.push({key: k, value: average_alerts[k]/res.length, color: alert_to_color[k]})
                total -= average_alerts[k]/res.length
            }
            pie_data.push({key: "NO_ALERT", value: total, color: "green"})
            this.setState({uptime: uptime, prev_uptime: this.state.uptime, pie_data: pie_data, uptime_history: [...this.state.uptime_history, {x: this.state.uptime_history.length + 1, y: uptime}]})
        })
      setTimeout(this.getData, 5000)
    }

    componentWillMount(){
        fetch(URL+"/result/uptime_history")
        .then(res => res.json())
        .then(res => res.map( (value, i) => ({x: i, y: value}) )) 
        .then(res => this.setState({"uptime_history": res}))
        fetch(URL+"/result/energy_history")
        .then(res => res.json())
        .then(res => res.map( (value, i) => ({x: i, y: value}) )) 
        .then(res => this.setState({"energy_history": res}))
        this.getData()
    }

    render(){
        return (
        <div className="container">
        <div className="jumbotron">
                <h2 className="display-4">Your system performance, in a nutshell</h2>
                <div className="container">
                    <div className="row">
                        <div className="col-sm">
                            <Number title="Energy Consumption" start={this.state.prev_cost} value={this.state.cost} decimals={2} suffix=" kWh (<i>monthly</i>)"/>
                        </div>
                        <div className="col-sm">
                            <Number title="Mean Uptime" start={this.state.prev_uptime*100} decimals={2} value={this.state.uptime*100} suffix=" %" />
                        </div>
                        <div className="col-sm">
                            <Number title="Mean Downtime" start={100-(this.state.prev_uptime*100)} decimals={2} value={100-(this.state.uptime*100)} suffix=" %"/>
                        </div>
                    </div>
                    <hr className="my-4"/>
                    <div className="row">
                        <div className="col-sm">
                            <h2>Uptime</h2>
                            <LineChart
                                axes
                                yAxisOrientLeft
                                width={450}
                                height={150}
                                yDomainRange={[0, 1]}
                                yTicks={3}
                                xTicks={1}
                                data={[this.state.uptime_history]}
                            />
                            <h2>Energy Consumption</h2>
                            <LineChart
                                axes
                                yAxisOrientLeft
                                width={450}
                                height={150}
                                yTicks={3}
                                xTicks={1}
                                data={[this.state.energy_history]}
                            />
                        </div>
                        <div className="col-sm">
                            <h3>Alert Type Summary</h3>
                            <table className="quadretto">
                                    <tbody><tr>
                                    <td>
                                        <PieChart
                                            key={"pie"}
                                            id={"pie-chart"}
                                            size={200}
                                            innerHoleSize={0}
                                            data={this.state.pie_data}
                                        />
                                    </td>
                                    <td>
                                        <Quadretti data={this.state.pie_data.map(val => { return {color: val.color, val: val.value*100, name: val.key}} )} />
                                    </td>
                                    </tr>
                                    </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                
        </div></div>)
    }
}