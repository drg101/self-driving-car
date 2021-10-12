import React, { useEffect, useState } from 'react';
import logo from './logo.svg';
import './App.css';
import { Grid } from '@material-ui/core'
import ControlPad from './control-pad/ControlPad'
import NoSignal from "./assets/nosignal.png"
import { io } from "socket.io-client";

const SERVER_IP = '192.168.80.58'

const socket = io(`http://${SERVER_IP}:8002`, {
    reconnectionDelayMax: 10000
});

socket.on('test', (e) => { console.log(`Recieved ${e}`) })

type ControlTernary = -1 | 0 | 1;
export interface ControlState {
    fw: ControlTernary,
    lr: ControlTernary
}
let oldControl = {}
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
        if (JSON.stringify(control) !== JSON.stringify(oldControl)) {
            console.log({ control })
            socket.emit('my_event', JSON.stringify(control))
            oldControl = control;
        }
    }, [control])

    useEffect(() => {
        function logKey(e: KeyboardEvent, upDown: 0 | 1) {
            switch (e.code) {
                case "KeyW":
                    if (upDown === 0 && control.fw === -1) {
                        break;
                    }
                    setControl({ ...control, fw: upDown })
                    break;
                case "KeyA":
                    if (upDown === 0 && control.lr === 1) {
                        break;
                    }
                    setControl({ ...control, lr: -upDown as ControlTernary })
                    break;
                case "KeyS":
                    if (upDown === 0 && control.fw === 1) {
                        break;
                    }
                    setControl({ ...control, fw: -upDown as ControlTernary })
                    break;
                case "KeyD":
                    if (upDown === 0 && control.lr === -1) {
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
                                <img src={`http://${SERVER_IP}:8003/video_feed`} style={{ width: "100%", height: "100%" }} />
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
