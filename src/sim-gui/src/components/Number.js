import React from "react"
import AnimatedNumber from "animated-number-react";

export default class Number extends React.Component{
    render(){
        console.log("stability number inside", this.props.stability)
        return <div><h3>{this.props.title}</h3>
            <font size="3" color={"black"}><AnimatedNumber value={this.props.value} formatValue={ this.props.formatValue } /></font></div>
    }
}
