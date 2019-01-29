import React, { Component } from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.css';
import { Nav, NavItem, NavLink} from 'reactstrap';
import { BrowserRouter as Router, Route } from "react-router-dom";
import DevicesTable from "./components/DevicesTable"
import MyAppsTable from "./components/MyAppsTable"
import Certificate from './components/Certificate';
import { URL } from "./costants"
import CountUp from 'react-countup';

const simCounter_updateTime = 2000

class App extends Component {
  constructor(props){
    super(props)
    this.state = {counter: 0, prev_counter: 0, counter_loading: true}
  }

  setCounter = () => {
    fetch(URL+"/result/simulationcounter")
    .then(res =>  res.text())
    .then(res => this.setState({counter_loading: false, counter: parseInt(res), prev_counter: this.state.counter_loading ? parseInt(res-20) : this.state.counter}))
    setTimeout(this.setCounter, simCounter_updateTime)
  }

  componentWillMount(){
    this.setCounter()
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
    <NavLink>Simulation Iteration Counter: {this.state.counter_loading ? <i>loading</i> : <CountUp start={this.state.prev_counter} easingFn={(t,b,c,d) => b+c*(t/d)} end={this.state.counter} duration={simCounter_updateTime/2000+1}/>}</NavLink>
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
