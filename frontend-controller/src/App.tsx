import React, { useEffect, useState } from 'react';
import logo from './logo.svg';
import './App.scss';
import { Grid } from '@material-ui/core'
import VideoStream from './video-stream/VideoStream'
import ControlPad from './control-pad/ControlPad'
import NoSignal from "./assets/nosignal.png"
// import { io } from "socket.io-client";

// const socket = io("http://0.0.0.0:8002", {
//     reconnectionDelayMax: 10000
// });

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

    const [image, setImage] = useState(new Image())

    useEffect(() => {
        const newImg = new Image();
        newImg.onload = () => {
            setImage(newImg)
        }
        newImg.src = `${NoSignal}`
    })

    useEffect(() => {
        function logKey(e: KeyboardEvent, upDown: 0 | 1) {
            switch (e.code) {
                case "KeyW":
                    if(upDown === 0 && control.fw === -1) {
                        break;
                    }
                    setControl({ ...control, fw: upDown })
                    break;
                case "KeyA":
                    if(upDown === 0 && control.lr === 1) {
                        break;
                    }
                    setControl({ ...control, lr: -upDown as ControlTernary })
                    break;
                case "KeyS":
                    if(upDown === 0 && control.fw === 1) {
                        break;
                    }
                    setControl({ ...control, fw: -upDown as ControlTernary })
                    break;
                case "KeyD":
                    if(upDown === 0 && control.lr === -1) {
                        break;
                    }
                    setControl({ ...control, lr: upDown })
                    break;
            }
        }
        const onKeyDown = (e: KeyboardEvent) => { logKey(e, 1) }
        const onKeyUp = (e: KeyboardEvent) => { logKey(e, 0) }
        document.onkeydown = onKeyDown;
        document.onkeyup = onKeyUp;
    }, [control])

    return (
        <div className="App">
            <Grid container style={{ height: "100%" }}>
                <Grid item xs={8}>
                    <Grid container>
                        <Grid item xs={12}>
                            <div style={{ height: "60vh" }}>
                                <VideoStream image={image}/>
                            </div>
                        </Grid>
                        <Grid item xs={12}>
                            <div style={{ height: "40vh" }}>
                                <ControlPad orientation="left-right" control={control} setControl={setControl} />
                            </div>
                        </Grid>
                    </Grid>
                </Grid>
                <Grid item xs={4}>
                    <div style={{ height: "100vh" }}>
                        <ControlPad orientation="up-down" control={control} setControl={setControl} />
                    </div>
                </Grid>
            </Grid>
        </div>
    );
}

export default App;
