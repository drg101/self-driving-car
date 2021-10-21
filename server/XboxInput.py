from inputs import devices, get_gamepad
import threading

fw = 0
bk = 0
lr = 0

def get_inputs():
    return {'fw': fw - bk, 'lr': lr}

def poll(onChange):
    global fw,bk,lr
    while True:
        change = False
        events = get_gamepad()
        for event in events:
            if event.code == "ABS_RZ":
                # print(f"FW: {event.state / 1023}")
                change = True
                fw = event.state / 1023
            elif event.code == "ABS_Z":
                # print(f"BK {event.state / 1023}")
                change = True
                bk = event.state / 1023
            elif event.code == "ABS_X":
                # print(f"LR: {event.state / 32768}")
                change = True
                lr  = event.state / 32768
        if change:
            onChange(get_inputs())

def begin_polling(onChange):
    threading.Thread(target=poll, args=[onChange]).start()
    print("began polling for xbox inputs")