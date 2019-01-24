import React from 'react';
import { URL } from "../costants"
import Number from "./Number"

export default class Certificate extends React.Component {
    constructor(props){
        super(props)
        this.state = {cost: 0, uptime: 0, downtime: 0}
    }

    getData = () => {
      fetch(URL+"/result/devices")
        .then(res => res.json())
        .then(res => res.reduce((prev, current) => (prev+current.DEVICE_ENERGY_CONSUMPTION), 0))
        .then(cost => this.setState({cost: cost}))
        .catch(err => alert("DeviceTable Fetch Error "+err))
      fetch(URL+"/result/myapps")
        .then(res => res.json())
        .then(res => res.reduce((prev, current) => (prev+current.UP_PERCENTAGE), 0) / res.length ) 
        .then(uptime => this.setState({uptime: uptime, downtime: 1-uptime}))
        .catch(err => alert("DeviceTable Fetch Error "+err))
      setTimeout(this.getData, 5000)
    }

    componentWillMount(){
        console.log("certificate will mount")
        this.getData()
    }
    componentWillUpdate(){
        console.log("certificate will update")
    }
    render(){
        return (
        <div className="jumbotron">
                <h1 className="display-4">Your system result, in a nutshell!</h1>
                <div className="container">
                    <div className="row">
                        <div className="col-sm">
                            <Number title="Total Cost" value={Math.round(this.state.cost*10000)/100} formatValue={(val => (val.toFixed(2)+" W/month"))}/>
                        </div>
                        <div className="col-sm">
                            <Number title="Mean Uptime" value={Math.round(this.state.uptime*10000)/100} formatValue={(val => (val.toFixed(2)+" %"))}/>
                        </div>
                        <div className="col-sm">
                            <Number title="Mean Downtime" value={Math.round(this.state.downtime*10000)/100} formatValue={(val => (val.toFixed(2)+" %"))}/>
                        </div>
                    </div>
                </div>
                <hr className="my-4"/>
                <p>In order to see detailed information...</p>
                <p className="lead">
                    <a className="btn btn-primary btn-lg" href="/devices" role="button" style={{margin: "10px"}} >Devices</a>
                    <a className="btn btn-primary btn-lg" href="/myapps" role="button">MyApps</a>
                </p>
        </div>)
    }
}