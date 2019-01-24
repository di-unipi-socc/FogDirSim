import React from "react"
import AnimatedNumber from "animated-number-react";

export default class Number extends React.Component{
    render(){
        return <div><h3>{this.props.title}</h3><AnimatedNumber value={this.props.value} formatValue={ this.props.formatValue } /></div>
    }
}
