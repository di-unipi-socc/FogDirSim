import React from "react"
import {Progress} from "reactstrap"

export default class MyAppDevice extends React.Component{
    render(){
        return <div className="myAppDeviceGrid">
            <div style={{gridArea:"deviceId"}}>DevId: {this.props.deviceId}</div><div style={{gridArea:"timeInstalled"}}>Inst. Time: {this.props.time.toFixed(2)} %</div>
            <Progress multi style={{gridArea:"start"}}>
                <Progress bar color="success" value={this.props.start.toFixed(2)}>{this.props.start.toFixed(2)}</Progress>
                <Progress bar color="danger" value={this.props.stop.toFixed(2)}>{this.props.stop.toFixed(2)}</Progress>
            </Progress>
        </div>
    }
}