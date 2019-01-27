import React from 'react';
import { URL } from "../costants"
import Number from "./Number"

export default class Certificate extends React.Component {
    constructor(props){
        super(props)
        this.state = {cost: 0, prev_cost: -1000, uptime: 0, prev_uptime: -1000, downtime: 0}
    }

    getData = () => {
      fetch(URL+"/result/devices")
        .then(res => res.json())
        .then(res => res.reduce((prev, current) => (prev+current.DEVICE_ENERGY_CONSUMPTION), 0))
        .then(cost => this.setState({cost: cost, prev_cost: this.state.cost}))
      fetch(URL+"/result/myapps")
        .then(res => res.json())
        //.then(res => console.log(res))
        .then(res => res.reduce((prev, current) => (prev+current.UP_PERCENTAGE), 0) / res.length ) 
        .then(uptime => this.setState({uptime: uptime, prev_uptime: this.state.uptime, downtime: 1-uptime}))

      setTimeout(this.getData, 10000)
    }

    componentWillMount(){
        console.log("certificate will mount")
        this.getData()
    }
    componentWillUpdate(){
        console.log("certificate will update")
    }
    render(){
        let uptime_stability = false
        let cost_stability = false
        console.log(this.state.uptime)
        if (Math.abs(this.state.uptime - this.state.prev_uptime) < 0.05){
            uptime_stability = true
        }
        if (Math.abs(this.state.cost - this.state.prev_cost) < 100){
            cost_stability = true
        }
        console.log(uptime_stability)
        return (
        <div className="container">
        <div className="jumbotron">
                <h2 className="display-4">Your system performance, in a nutshell</h2>
                <div className="container">
                    <div className="row">
                        <div className="col-sm">
                            <Number title="Total Cost" stability={cost_stability} value={Math.round(this.state.cost*10000)/100} formatValue={(val => (val.toFixed(2)+" kWh/month"))}/>
                        </div>
                        <div className="col-sm">
                            <Number title="Mean Uptime" stability={uptime_stability} value={Math.round(this.state.uptime*10000)/100} formatValue={(val => (val.toFixed(2)+" %"))}/>
                        </div>
                        <div className="col-sm">
                            <Number title="Mean Downtime"  stability={uptime_stability} value={Math.round(this.state.downtime*10000)/100} formatValue={(val => (val.toFixed(2)+" %"))}/>
                        </div>
                    </div>
                </div>
                <hr className="my-4"/>
                <p>In order to see detailed information...</p>
                <p className="lead">
                    <a className="btn btn-primary btn-lg" href="/devices" role="button" style={{margin: "10px"}} >Devices</a>
                    <a className="btn btn-primary btn-lg" href="/myapps" role="button">MyApps</a>
                </p>
        </div></div>)
    }
}