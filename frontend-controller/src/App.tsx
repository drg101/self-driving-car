import React from 'react';
import logo from './logo.svg';
import './App.css';
import { Grid } from '@material-ui/core'

type ControlTernary = -1 | 0 | 1;
interface ControlState {
    fw: ControlTernary,
    lr: ControlTernary
}

function App() {
    return (
        <div className="App">
            <Grid container>
                <Grid item xs={12} md>

                </Grid>
                <Grid item>

                </Grid>
            </Grid>
        </div>
    );
}

export default App;
