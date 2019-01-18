import React from 'react';
import { FormGroup, Label, Input, Card, CardImg, CardBody, CardTitle, CardSubtitle, InputGroup, InputGroupAddon } from 'reactstrap';
import { URL } from "../costants"

export default class CostPanel extends React.Component {
    constructor(props){
        super(props)
        this.state = {deviceMyApps: [], myapps: [], devices: [], deviceCost: {} }
        this.createState = this.createState.bind(this)
    }

    createState(res){
        console.log(res)
        let myapps = new Set()
        let devices = new Set()
        res.forEach(el => {myapps.add(el.myappId); devices.add(el.deviceId)})
        this.setState({deviceMyApps: res, myapps: Array.from(myapps), devices: Array.from(devices)})
    }

    componentWillMount(){
        fetch(URL+"/result/myappsstartstopdevice")
            .then(res => res.json())
            .then(res => this.createState(res))
    }

    render(){
        return <div className="container">
            <FormGroup>
                <Label for="myapps">Select MyApps</Label>
                <Input type="select" name="select" id="myapps" onChange={e => this.setState({selectedMyapp: e})}>
                    {this.state.myapps.map(e => <option key={e} value={e}>{e}</option>)}
                </Input>
            </FormGroup>
        </div>
    }
}