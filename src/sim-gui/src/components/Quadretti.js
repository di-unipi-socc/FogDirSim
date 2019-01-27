import React from "react"

export default class Quadretti extends React.Component{

    render(){
        return <div className="quadretto" style={{width: "300px"}}>
            {
                this.props.data.map(value => 
                    <p style={{lineHeight: "3px"}} key={value.name.toLowerCase()}><font color={value.color}>
                        &#9632; {value.val.toFixed(2)} % {value.name.toLowerCase()}</font>
                    </p>
                )
            }
        </div>
    }
}