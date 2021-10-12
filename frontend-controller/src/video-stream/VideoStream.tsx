import React, { useRef, useEffect } from 'react';
import { Grid } from '@material-ui/core'

interface VideoStreamProps {
    socket: any
}
let oldTime = 0

export default function VideoStream(props: VideoStreamProps) {
    const playerRef = useRef(null as unknown as HTMLImageElement)
    useEffect(() => {
        props.socket.on('imgFrame', (e: string) => {
            // console.log(Date.now() - oldTime)
            // oldTime = Date.now()
            const b64 = 'data:image/jpeg;base64,' + e.substr(2,e.length-3)
            if(playerRef.current) {
                playerRef.current.src = b64;
            } 
            // console.log({b64})
            // const image = new Image();
            // image.onload = () => {
            //     ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height)
            //     ctx.drawImage(image, 0,0, ctx.canvas.width, ctx.canvas.height)
            // }
            // image.src = b64;
        })
    }, [])

    return <img ref={playerRef} style={{ width: "100%", height: "100%" }} />
}

