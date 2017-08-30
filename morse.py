#The following code, executed on Raspberry Pi 3, will allow user to 1.) display a message in morse code with an LED bulb and 2.)enter morse code onto computer using a button. 

from gpiozero import Button,LED
from time import sleep
from signal import pause
import time

button = Button(2)
led = LED(17)

def check_range(max,min):
    '''
    returns the percentage the maximum and minimum of a set of numbers deviate from the median
    '''
    middle = (max+min)/2
    return (max-middle)/middle

def dot():
    '''
    makes LED bulb flash a dot in standard morse code
    '''
    led.on()
    sleep(0.1)
    led.off()
    sleep(0.1)

def dash():
    '''
    makes LED bulb flash a dash in standard morse code
    '''
    led.on()
    sleep(0.3)
    led.off()
    sleep(0.1)
    
def space():
    '''
    makes LED bulb display a space in standard morse code
    '''
    led.off()
    sleep(0.5)

def gap():
    '''
    makes LED bulb display a gap in standard morse code
    '''
    led.off()
    sleep(0.2)

def execute(func_list):
    '''
    executes a list of functions
    '''
    for f in func_list:
        f()
    gap()

#dictionary containing the function list for each symbol in morse code to be executed
morse = {'a':[dot,dash],'b':[dash,dot,dot,dot],'c':[dash,dot,dash,dot],'d':[dash,dot,dot],'e':[dot],'f':[dot,dot,dash,dot],'g':[dash,dash,dot],'h':[dot,dot,dot,dot],'i':[dot,dot],'j':[dot,dash,dash,dash],'k':[dash,dot,dash],'l':[dot,dash,dot,dot],'m':[dash,dash],'n':[dash,dot],'o':[dash,dash,dash],'p':[dot,dash,dash,dot],'q':[dash,dash,dot,dash],'r':[dot,dash,dot],'s':[dot,dot,dot],'t':[dash],'u':[dot,dot,dash],'v':[dot,dot,dot,dash],'w':[dot,dash,dash],'x':[dash,dot,dot,dash],'y':[dash,dot,dash,dash],'z':[dash,dash,dot,dot],'1':[dot,dash,dash,dash,dash],'2':[dot,dot,dash,dash,dash],'3':[dot,dot,dot,dash,dash],'4':[dot,dot,dot,dot,dash],'5':[dot,dot,dot,dot,dot],'6':[dash,dot,dot,dot,dot],'7':[dash,dash,dot,dot,dot],'8':[dash,dash,dash,dot,dot],'9':[dash,dash,dash,dash,dot],'0':[dash,dash,dash,dash,dash],' ':[space]}

def in_dot(mean_dot,time):
    '''
    Checks if time button is held down for is a dot. Returns True if time within 40% of mean dot time, False otherwise
    '''    
    low = 0.6*mean_dot
    high = 1.4*mean_dot
    if low<time<high:
        return True
    return False 
    
def in_dash(mean_dash,time):
    '''
    Checks if time button is held down for is a dash. Returns True if time within 40% of mean dash time, False otherwise
    '''
    low = 0.6*mean_dash
    high = 1.4*mean_dash
    if low<time<high:
        return True
    return False

def is_space(space_time,time):
    '''
    Checks if time button held down for is a space. Return True if time held down for is longer than 60% of the mean space time.
    '''
    low = 0.6*space_time
    if low<time:
        return True
    return False

def read_morse(L,morse):
    '''
    takes a list of how long button is held down and released (negative for released, positive for held down) and returns a string corresponding to the morse code sequence the list represents
    '''
    str = ''
    total_time = 0
    count = 0
    dot_time = 0
    dash_time = 0
    dot_count = 0
    dash_count = 0
    max_time = 0
    min_time = 1000000000
        
    #calculate mean time button was held for
    for time in L: 
        if time > 0:
            total_time += time
            count +=1
            if time > max_time:
                max_time = time
            if time < min_time:
                min_time = time
    mean = total_time / count

    #checks if all signals are either dots or dashes, assigns value to dots and dashes accordingly
    if check_range(max_time,min_time) < 0.4: #if all time held down for is within 40% of each other, they are all either dots or dashes. 
        if mean >= 0.3:
            mean_dash = mean
            mean_dot = 0
            space_time= 2.33*mean_dash
        if mean < 0.3:
            mean_dot = mean
            mean_dash = 0
            space_time = 7*mean_dot
    else: #otherwise, calculate mean dot time and mean dash time by taking the mean of all times below the mean (dots) and above the mean (dashes)
        for time in L:
            if time > 0:
                if time <= mean:
                    dot_time += time
                    dot_count += 1
                if time > mean:
                    dash_time += time
                    dash_count += 1

        mean_dot = dot_time / dot_count
        mean_dash = dash_time / dash_count
        space_time = 7*mean_dot

    #print(mean_dot,mean_dash)

    s_list = []
    final = []
    
    #creates list of lists with each sub-list representing a morse sequence for a letter, number, or space 
    for time in L:
        if time > 0:
            if in_dot(mean_dot,time):
                s_list.append(dot)
            elif in_dash(mean_dash,time):
                s_list.append(dash)
        if time < 0:
            if in_dash(mean_dash,abs(time)):
                final.append(s_list)
                s_list = []
            elif is_space(space_time,abs(time)):
                final.append(s_list)
                s_list = []
                final.append([space])
    final.append(s_list)

    #translates morse sequence to a string
    for l in final:
        for item in morse:
            if morse[item] == l:
                str += item

    return str
    
def morse_to_english():
    '''
    takes user inputted sequence from button and prints corresponding message in english
    '''
    
    L = []  # sequential list of times button was held and unheld
    initial = 0
    final = 0
    
    #user imputs morse code
    while True:
        button.when_pressed = led.on
        button.wait_for_press()
        initial = time.time()
        L.append(final-initial) #time button released will be recorded as negative
        button.when_released = led.off
        button.wait_for_release()
        final = time.time()
        L.append(final - initial)
        if (abs(final-initial) > 2): #to terminate, hold button for 3 seconds
            break

    L = L[1:-1] #splicing removes time before button is first pressed and termination sequence
    print(read_morse(L,morse))

def english_to_morse():
    '''
    takes a user inputted message and displays it in morse code with LED
    '''
    
    output = input('enter message in all lower case')
    for i in range(len(output)):
        execute(morse[output[i]])

def display_input():
    '''
    takes sequence user taps on button and replays it with LED
    '''
    L = []  # sequential list of times button was held and unheld
    initial = 0
    final = 0
    
    #user imputs morse code
    while True:
        button.when_pressed = led.on
        button.wait_for_press()
        initial = time.time()
        L.append(final-initial) #time button will be recorded as negative
        button.when_released = led.off
        button.wait_for_release()
        final = time.time()
        L.append(final - initial)
        if (abs(final-initial) > 2): #to terminate, hold button for 3 seconds
            break

    L = L[1:-1]
    for item in L:
        if item > 0:
            led.on()
            sleep(item)
            led.off()
        if item < 0:
            led.off()
            sleep(-item)
            led.off()

if __name__=='__main__':
    morse_to_english()
    #english_to_morse()
    #display_input()