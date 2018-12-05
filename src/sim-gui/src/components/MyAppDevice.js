import React from "react"

export default class MyAppDevice extends React.Component{
    render(){
        return <div className="myAppDeviceGrid">
            <div style={{gridArea:"deviceId"}}>DevId: {this.props.deviceId}</div><div style={{gridArea:"timeInstalled"}}>Inst. Time: {this.props.time.toFixed(2)} %</div>
            <div style={{gridArea:"start"}}>Run: {this.props.start.toFixed(2)} %</div>
            <div style={{gridArea:"stop"}}>Stop: {this.props.stop.toFixed(2)} %</div>
        </div>
    }
}