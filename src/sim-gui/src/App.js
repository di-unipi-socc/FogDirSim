import React, { Component } from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.css';
import { Nav, NavItem, NavLink} from 'reactstrap';
import { BrowserRouter as Router, Route } from "react-router-dom";
import DevicesTable from "./components/DevicesTable"
import MyAppsTable from "./components/MyAppsTable"
import Certificate from './components/Certificate';
import { URL } from "./costants"
import AnimatedNumber from "animated-number-react";

class App extends Component {
  constructor(props){
    super(props)
    this.state = {counter: 0}
    this.setCounter()
  }

  setCounter = () => {
    fetch(URL+"/result/simulationcounter")
    .then(res =>  res.text())
    .then(res => this.setState({counter: res}))
    setTimeout(this.setCounter, 2000)
  }

  componentWillMount(){
  }

  render() {
    return (
      <Router>
        <div className="col-lg-12">
        
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
          <Nav className="justify-content-center">
            <NavItem>
              <NavLink>Simulation Iteration Counter: <AnimatedNumber value={this.state.counter} duration={1000} formatValue={val => Math.round(val)}/></NavLink>
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
