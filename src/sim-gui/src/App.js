import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import 'bootstrap/dist/css/bootstrap.css';
import { Nav, NavItem, NavLink, Card, CardBody, CardImg, CardText, CardTitle, Button} from 'reactstrap';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
import DevicesTable from "./components/DevicesTable"
import MyAppsTable from "./components/MyAppsTable"
import Certificate from './components/Certificate';

class App extends Component {
  render() {
    return (
      <Router>
        <div className="container">
          <Nav className="justify-content-center">
            <NavItem>
              <NavLink href="/">Home</NavLink>
            </NavItem>
            <NavItem >
              <NavLink href="/devices">Devices</NavLink>
            </NavItem>
            <NavItem>
              <NavLink href="/myapps">MyApps</NavLink>
            </NavItem>
          </Nav>
          <Route path="/" exact component={Certificate} />
          <Route path="/devices/" component={DevicesTable} />
          <Route path="/myapps/" component={MyAppsTable} />
        </div>
      </Router>
    );
  }
}

export default App;
