import React, { useRef, useEffect } from 'react';
import { Grid } from '@material-ui/core'
import './ControlPad.css'

interface ControlPadProps {
    orientation: "up-down" | "left-right"
}

export default function ControlPadFw(props: ControlPadProps) {
    const padWidth = props.orientation === "up-down" ? 12 : 6;
    const padHeight = props.orientation === "up-down" ? "50%" : "100%";
    return <Grid container style={{height: "100%"}}>
        <Grid item xs={padWidth} className="pad" style={{height: padHeight}}>
            
        </Grid>
        <Grid item xs={padWidth} className="pad" style={{height: padHeight}}>
            
        </Grid>
    </Grid>
}

