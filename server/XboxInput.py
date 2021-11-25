from inputs import devices, get_gamepad
import threading

fw = 0
bk = 0
lr = 0

EPSILON = 0.03

def getLr():
    if lr > 0.01:
        return 1
    elif lr < -0.01:
        return -1
    return 0

def get_inputs():
    return {'fw': round(fw - bk,2), 'lr': getLr()}

def poll(onChange):
    global fw,bk,lr
    while True:
        events = get_gamepad()
        newfw = fw
        newbk = bk
        newlr = lr
        for event in events:
            if event.code == "ABS_RZ":
                # print(f"FW: {event.state / 1023}")
                newfw = round(event.state / 1023,2) * 0.5
            elif event.code == "ABS_Z":
                # print(f"BK {event.state / 1023}")
                newbk = round(event.state / 1023,2)
            elif event.code == "ABS_X":
                # print(f"LR: {event.state / 32768}")
                newlr  = round(event.state / 32768,2)
            elif event.code == 'ABS_HAT0X':
                newlr = event.state
                #print(event.code, event.state)
        if abs(get_inputs()['fw'] - (newfw - newbk)) > EPSILON or abs(get_inputs()['lr'] - (newlr)) > EPSILON or True:
            fw = newfw
            bk = newbk
            lr = newlr
            onChange(get_inputs())

def begin_polling(onChange):
    threading.Thread(target=poll, args=[onChange]).start()
    print("began polling for xbox inputs")