import React, { useRef, useEffect } from 'react';
import { Grid } from '@material-ui/core'

export default function VideoStream() {
    const canvasRef = useRef(null as unknown as HTMLCanvasElement)
    useEffect(() => {
        const canvas = canvasRef.current;
        if(!canvas) {
            return;
        }
        const ctx = canvas.getContext('2d')
        if(!ctx) {
            return;
        }
        //Our first draw
        ctx.fillStyle = '#000000'
        ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height)
    }, [])

    return <canvas ref={canvasRef} style={{width: "100%", height: "100%"}}/>
}

