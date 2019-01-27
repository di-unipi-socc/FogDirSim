import React from "react"

export default class MyAppDevice extends React.Component{
    render(){
        return <div className="myAppDeviceGrid">
            <div style={{gridArea:"deviceId"}}>DevId: {this.props.deviceId}</div><div style={{gridArea:"timeInstalled"}}>Runned: {this.props.time.toFixed(2)} %</div>
            <div className="progress" style={{gridArea:"start"}}>
                <div className="progress-bar bg-success" role="progressbar" style={{width: this.props.startTime+"%"}} aria-valuenow="15" aria-valuemin="0" aria-valuemax="100">{this.props.startTime > 10 ? this.props.startTime.toFixed(2) + "%" : "" }</div>
                <div className="progress-bar bg-danger" role="progressbar" style={{width: 100-this.props.startTime+"%"}} aria-valuenow="15" aria-valuemin="0" aria-valuemax="100">{this.props.startTime < 90 ? (100-this.props.startTime).toFixed(2) + "%" : "" }</div>
            </div>
        </div>
    }
}