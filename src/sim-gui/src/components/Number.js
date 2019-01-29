import React from "react"
import CountUp from 'react-countup';

export default class Number extends React.Component{
    render(){
        return <div><h3>{this.props.title}</h3>
            <font size="3" color={"black"}><CountUp start={this.props.start || 0} end={this.props.value} decimals={this.props.decimals} suffix={this.props.suffix} /></font></div>
    }
}
