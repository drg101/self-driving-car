import React, { useEffect, useState } from 'react';
import logo from './logo.svg';
import './App.css';
import { Grid } from '@material-ui/core'
import VideoStream from './video-stream/VideoStream'
import ControlPad from './control-pad/ControlPad'

type ControlTernary = -1 | 0 | 1;
export interface ControlState {
    fw: ControlTernary,
    lr: ControlTernary
}

function App() {
    const [control, setControl] = useState({
        fw: 0,
        lr: 0
    } as ControlState)

    
    return (
        <div className="App">
            <Grid container style={{ height: "100%" }}>
                <Grid item xs={8}>
                    <Grid container>
                        <Grid item xs={12}>
                            <div style={{height: "60vh"}}>
                                <VideoStream />
                            </div>
                        </Grid>
                        <Grid item xs={12}>
                            <div style={{height: "40vh"}}>
                                <ControlPad orientation="left-right" control={control} setControl={setControl}/>
                            </div>
                        </Grid>
                    </Grid>
                </Grid>
                <Grid item xs={4}>
                    <div style={{height: "100vh"}}>
                        <ControlPad orientation="up-down" control={control} setControl={setControl}/>
                    </div>
                </Grid>
            </Grid>
        </div>
    );
}

export default App;
