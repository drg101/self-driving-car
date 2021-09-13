import React, { useRef, useEffect } from 'react';
import { Grid } from '@material-ui/core'

interface VideoStreamProps {
    image: HTMLImageElement
}

export default function VideoStream(props: VideoStreamProps) {
    const canvasRef = useRef(null as unknown as HTMLCanvasElement)
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) {
            return;
        }
        const ctx = canvas.getContext('2d')
        if (!ctx) {
            return;
        }
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height)
        //Our first draw
        ctx.fillStyle = '#000000'
        ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height)
        ctx.drawImage(props.image, 0,0)
    })

    return <canvas ref={canvasRef} style={{ width: "100%", height: "100%" }} />
}

