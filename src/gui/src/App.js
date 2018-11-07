
import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
import './App.css';
import {Nav, Navbar, NavItem} from "react-bootstrap"
import Applications from "./components/Applications"
import Devices, {AddDeviceModal} from "./components/Devices"
import {wire, wire2} from "./styles"

const Index = () => <div style={{...wire2, paddingLeft: "10px"}}><center><h2>Hi! This is ALMOST Fog Director!</h2></center></div>

class App extends Component {
  constructor(props){
    super(props)
    this.state = {
      AddDeviceModalShow: false
    }
  }

  AddDeviceModalToggle = () => {
    this.setState({AddDeviceModalShow: !this.state.AddDeviceModalShow})
  }

  render() {
    return (
      <Router>
      <React.Fragment>
          <Navbar>
            <Navbar.Header>
              <Navbar.Brand>
                <Link to="/">FogDirector Simulator</Link>
              </Navbar.Brand>
            </Navbar.Header>
            <Nav>
              <NavItem componentClass={Link} to="/apps/" href="/apps/" eventKey={1}>
                APPS
              </NavItem>
              <NavItem componentClass={Link} to="/devices/" eventKey={2} href="/devices/">
                DEVICES
              </NavItem>
            </Nav>
          </Navbar>
        <div className="container">
          <Route path="/" exact component={Index} />
          <Route path="/apps/" component={Applications} />
          <Route path="/devices/" component={Devices} />
        </div>
        
      </React.Fragment>
      </Router>
    );
  }
}

export default App;
