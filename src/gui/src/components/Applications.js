
import React, { Component } from 'react';
import {Jumbotron, Row, Button, Modal, FormGroup, ControlLabel, HelpBlock, FormControl} from "react-bootstrap";
import {wire, wire2, wire3, wire4, wire5} from "../styles";

const FieldGroup = function({ id, label, help, ...props }) {
    return (
      <FormGroup controlId={id}>
        <ControlLabel>{label}</ControlLabel>
        <FormControl {...props} />
        {help && <HelpBlock>{help}</HelpBlock>}
      </FormGroup>
    );
}

export class AddApplicationModal extends Component{
    handleClose = () =>  {
        this.props.closeFun()
    }

    render(){
        return <Modal show={this.props.show} onHide={this.handleClose} style={wire}>
          <Modal.Header closeButton>
            <Modal.Title>Upload an application</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <form style={{...wire, padding: "20px"}}>
                <FieldGroup
                    id="file"
                    type="file"
                    label="File (.tar) of your application"
                />
            </form>
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={this.handleClose}>Close</Button>
          </Modal.Footer>
        </Modal>
    }
}

class InstalledApps extends Component{
    render(){
        return <Jumbotron style={wire2}>
            <Row>
                <h3>Installed Application</h3>
            </Row>
            <Row>
                Not yet
            </Row>
        </Jumbotron>
    }
}

class AvailableApps extends Component{
    render(){
        return <Jumbotron style={wire3}>
            <Row>
                <h3>Available Application</h3>
            </Row>
            <Row>
                Not yet
            </Row>
        </Jumbotron>
    }
}

class UnpublishedApps extends Component{
    constructor(props){
        super(props)
        this.state = {
            AddApplicationModalShow: false
        }
    }

    toggleAddModal = () => {
        this.setState({AddApplicationModalShow: !this.state.AddApplicationModalShow})
    }

    render(){
        return <React.Fragment>
            <AddApplicationModal show={this.state.AddApplicationModalShow} closeFun={this.toggleAddModal}/>
            <Jumbotron style={wire4}>
                <Row>
                    <h3 style={{display: "contents"}}>Installed Application</h3> <Button bsStyle="link" onClick={this.toggleAddModal}>Add New App</Button> 
                </Row>
                <Row>
                    Not yet
                </Row>
            </Jumbotron>
            </React.Fragment>
    }
}

export default class Applications extends Component {
    render(){
        return <React.Fragment>
            <InstalledApps/>
            <AvailableApps/>
            <UnpublishedApps/>

        </React.Fragment>
    }
}