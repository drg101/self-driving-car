import React from 'react';
import logo from './logo.svg';
import './App.css';
import { Grid } from '@material-ui/core'
import VideoStream from './video-stream/VideoStream'

type ControlTernary = -1 | 0 | 1;
interface ControlState {
    fw: ControlTernary,
    lr: ControlTernary
}

function App() {
    return (
        <div className="App">
            <Grid container>
                <Grid item xs={6}>
                    <div className="canvas-container">
                        <VideoStream />
                    </div>
                </Grid>
                <Grid item xs={6}>
                    <div className="controller-container">
                        
                    </div>
                </Grid>
            </Grid>
        </div>
    );
}

export default App;
