import React, { Component } from 'react';
import {Tooltip, OverlayTrigger, Table} from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faMicrochip, faMemory } from '@fortawesome/free-solid-svg-icons'
import {wire, wire2, wire3, wire4, wire5} from "../styles";

class CPUDeviceTooltip extends React.Component{
    constructor(props){
        super(props)
    }

    render(){
        return <Tooltip id={this.props.id}>
           CPU Usage {this.props.used} / {this.props.total}
        </Tooltip>
    }
}

class MemoryDeviceTooltip extends React.Component{
    constructor(props){
        super(props)
    }

    render(){
        return <Tooltip id={this.props.id} >
           Memory Usage {this.props.used} / {this.props.total}
        </Tooltip>
    }
}

export default class DevicesTable extends Component{
    constructor(props){
        super(props)
        this.state = {
            devices: [
                {
                    name: "Device 1",
                    ipAddress: "10.10.20.51",
                    port: "8443",
                    tags: ["BlueTag", "RedTag", "GreenTag"],
                    lastHeard: "5 minutes", 
                    cpuTotal: 2000,
                    cpuUsed: 1003,
                    memTotal: 2000,
                    memUsed: 1001
                },
                {
                    name: "Device 2",
                    ipAddress: "10.10.20.52",
                    port: "8443",
                    tags: ["VioletTag", "OrangeTag", "GreenTag"],
                    cpuTotal: 2000,
                    cpuUsed: 1004,
                    memTotal: 2000,
                    memUsed: 1002,
                    lastHeard: "5 minutes"
                }
            ]
        }
    }

    render(){
        return (<Table striped bordered condensed hover>
            <thead>
              <tr>
                <th>Name</th>
                <th>IP Address</th>
                <th>Tags</th>
                <th>Capacity</th>
                <th>Last Heard</th>
              </tr>
            </thead>
            <tbody>
                {this.state.devices.map(dev => {
                    return (<tr key={dev.ipAddress+":"+dev.port}>
                            <td>{dev.name}</td>
                            <td>{dev.ipAddress}</td>
                            <td>{dev.tags.map(tag => tag+" ")}</td>
                            <td>
                                <p>CPU: {dev.cpuUsed} / {dev.cpuTotal} </p>
                                <p>MEM: {dev.memUsed} / {dev.memTotal} </p>
                            </td>
                            <td>{dev.lastHeard}</td>
                        </tr>
                    )
                })}
            </tbody>
        </Table>)
    }
}