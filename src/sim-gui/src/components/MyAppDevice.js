import React from "react"
import {Progress} from "reactstrap"

export default class MyAppDevice extends React.Component{
    render(){
        return <div className="myAppDeviceGrid">
            <div style={{gridArea:"deviceId"}}>DevId: {this.props.deviceId}</div><div style={{gridArea:"timeInstalled"}}>Runned: {this.props.time.toFixed(2)} %</div>
        </div>
    }
}