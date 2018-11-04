import React, { Component } from 'react';
import {Jumbotron, Row, Button, Grid, Col, Modal, FormGroup, ControlLabel, FormControl, HelpBlock} from "react-bootstrap";
import {wire, wire2, wire3, wire4, wire5} from "../styles";
import DevicesTable from "./DevicesTable"

const FieldGroup = function({ id, label, help, ...props }) {
    return (
      <FormGroup controlId={id}>
        <ControlLabel>{label}</ControlLabel>
        <FormControl {...props} />
        {help && <HelpBlock>{help}</HelpBlock>}
      </FormGroup>
    );
}

export class AddDeviceModal extends Component{
    handleClose = () =>  {
        this.props.closeFun()
    }

    render(){
        return <Modal show={this.props.show} onHide={this.handleClose} style={wire}>
          <Modal.Header closeButton>
            <Modal.Title>Add a device</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <form style={{...wire, padding: "20px"}}>
                <FieldGroup
                    id="ipAddress"
                    type="text"
                    label="IP Address"
                    placeholder="xxx.xxx.xxx.xxx"
                />
                <FieldGroup
                    id="port"
                    type="number"
                    label="Port"
                    placeholder="nnnn"
                />
                <FieldGroup
                    id="username"
                    type="text"
                    label="Username"
                    placeholder="Enter Username"
                />
                <FieldGroup
                    id="password"
                    type="password"
                    label="Password"
                    placeholder="password"
                />
            </form>
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={this.handleClose}>Close</Button>
          </Modal.Footer>
        </Modal>
    }
}

export default class Devices extends Component{
    constructor(props){
        super(props)
        this.state = {
          AddDeviceModalShow: false
        }
    }

    AddDeviceModalToggle = () => {
        this.setState({AddDeviceModalShow: !this.state.AddDeviceModalShow})
    }
    render(){
        return <React.Fragment>
            <AddDeviceModal show={this.state.AddDeviceModalShow} closeFun={this.AddDeviceModalToggle}/>
            <h1>Devices</h1>
            <Grid>
                <Row>
                    <Col xs={12} md={4}>
                        <Jumbotron style={wire2}>
                            <h2>Reachability</h2>
                        </Jumbotron>
                    </Col>
                    <Col xs={12} md={4}>
                        <Jumbotron style={wire3}>
                            <h2>Last Heard</h2>
                        </Jumbotron>
                    </Col>
                    <Col xs={12} md={4}>
                        <Jumbotron style={wire4}>
                            <h2>Platform Version</h2>
                        </Jumbotron>
                    </Col>
                </Row>
                <Row style={{...wire3, padding: "20px"}}>
                    <Col md={4}>
                        <Button onClick={this.AddDeviceModalToggle}>Add New Device</Button>
                    </Col>
                </Row>
                <Row style={{...wire4, padding: "20px"}}>
                    <Col md={12}>
                        <DevicesTable/>
                    </Col>
                </Row>
            </Grid>
        </React.Fragment>
    }
}