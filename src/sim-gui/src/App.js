import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import 'bootstrap/dist/css/bootstrap.css';
import { Nav, NavItem, NavLink } from 'reactstrap';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
import DevicesTable from "./components/DevicesTable"
import MyAppsTable from "./components/MyAppsTable"

const Index = () => <h1>Fog Dir Simulator - Results</h1>

class App extends Component {
  render() {
    return (
      <Router>
        <div className="container">
          <Nav>
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
          <Route path="/" exact component={Index} />
          <Route path="/devices/" component={DevicesTable} />
          <Route path="/myapps/" component={MyAppsTable} />
        </div>
      </Router>
    );
  }
}

export default App;
