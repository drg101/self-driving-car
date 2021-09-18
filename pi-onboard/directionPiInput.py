import RPi.GPIO as GPIO
from control import forward, backward, left, right, straight, stop, setSpeed

direction_output = {
    'w': forward,
    'a': left,
    's': backward, 
    'd': right,
    ' ': stop,
    'e': straight
}


if __name__ == "__main__":
    setSpeed(100)
    print('Press q to exit.')
    while True:
        key = input('Enter a key: ')
        if key == 'q':
            print('exiting')
            break
        if key not in direction_output.keys():
            print('bad')
            continue
        func = direction_output[key]
        func()
    # reset direction on exit
    straight()

