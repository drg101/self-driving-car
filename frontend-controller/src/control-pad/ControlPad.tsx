import React, { useRef, useEffect } from 'react';
import { Grid } from '@material-ui/core'
import './ControlPad.css'
import { KeyboardArrowUp, KeyboardArrowDown, KeyboardArrowLeft, KeyboardArrowRight } from '@material-ui/icons';
import { ControlState } from "../App"

interface ControlPadProps {
    orientation: "up-down" | "left-right",
    control: ControlState,
    setControl: React.Dispatch<React.SetStateAction<ControlState>>
}

export default function ControlPad(props: ControlPadProps) {
    const upDown = props.orientation === "up-down";
    const padWidth = upDown ? 12 : 6;
    const padHeight = upDown ? "50%" : "100%";
    const controlStateId = upDown ? "fw" : "lr";
    const state = props.control[controlStateId]
    const handleMouseEvent = (enable: boolean, padId: 0 | 1) => {
        //lmao
        const newValue = enable ? (upDown ? (padId ? -1 : 1) : (padId ? 1 : -1)) : 0;
        props.setControl({...props.control, [controlStateId]: newValue});
    }

    return <Grid container style={{ height: "100%" }}>
        <Grid item xs={padWidth} className="pad" style={{ height: padHeight, backgroundColor: state === (upDown ? 1 : -1) ? "grey" : "white"}}
            onMouseDown={(e) => {
                handleMouseEvent(true, 0)
            }}
            onMouseUp={(e) => {
                handleMouseEvent(false, 0)
            }}
            onMouseLeave={(e) => {
                handleMouseEvent(false, 0)
            }}
            onTouchStart={(e) => {
                handleMouseEvent(true, 0)
            }}
            onTouchEnd={(e) => {
                handleMouseEvent(false, 0)
            }}
            // onTouchCancel={(e) => {
            //     handleMouseEvent(false, 0)
            // }}
        >
            <div className="padIconContainer">
                {upDown ? <KeyboardArrowUp fontSize="large" className="padIcon" /> : <KeyboardArrowLeft fontSize="large" className="padIcon" />}
            </div>
        </Grid>
        <Grid item xs={padWidth} className="pad" style={{ height: padHeight, backgroundColor: state === (upDown ? -1 : 1) ? "grey" : "white" }}
            onMouseDown={(e) => {
                handleMouseEvent(true, 1)
            }}
            onMouseUp={(e) => {
                handleMouseEvent(false, 1)
            }}
            onMouseLeave={(e) => {
                handleMouseEvent(false, 1)
            }}
            onTouchStart={(e) => {
                handleMouseEvent(true, 1)
            }}
            onTouchEnd={(e) => {
                handleMouseEvent(false, 1)
            }}
            // onTouchCancel={(e) => {
            //     handleMouseEvent(false, 1)
            // }}
        >
            <div className="padIconContainer">
                {upDown ? <KeyboardArrowDown fontSize="large" className="padIcon" /> : <KeyboardArrowRight fontSize="large" className="padIcon" />}
            </div>
        </Grid>
    </Grid>
}

