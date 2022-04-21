import pyautogui as py
import threading
import random
import sys
import time
from datetime import datetime, timedelta
import json
from PIL import Image
import hashlib

def look_for_bracket(l):
    '''locating brackets'''
    loc = py.locateOnScreen('line.png',region=(910,450,100,400),confidence=0.9)     #suitable for 1920*1080 24' display
    if not loc:
        return None

    loc = py.center(loc)
    x,y = loc
    #y_incre = random.choice(l)
    return 868,y+random.randint(5,15)

def look_for_tryagain():
    '''locate try again sign'''
    loc = py.locateOnScreen('tryagain.png',region=(1000,600,300,200),confidence=0.9)
    if not loc:
        return None
    
    loc = py.center(loc)
    x,y = loc
    return x+random.randint(-30,30),y

def look_for_begin():
    '''locate begin sign'''
    loc = py.locateOnScreen('begin.png',region=(1000,800,180,300),confidence=0.9)
    if not loc:
        return None
    
    loc = py.center(loc)
    x,y = loc
    return x+random.randint(-30,30),y

def rest():
    '''locate the sign above try again, which tells you either log out and retry or rest for a long time'''
    #normal
    win = py.locateOnScreen('win.png',region=(900,500,400,200),confidence=0.9)
    lose = py.locateOnScreen('lose.png',region=(900,500,400,200),confidence=0.9)
    if win or lose:
        return 'continue'
    #rest for a long time
    rest_w = py.locateOnScreen('rest_win.png',region=(900,500,400,200),confidence=0.9)
    rest_l = py.locateOnScreen('rest_lose.png',region=(900,500,400,200),confidence=0.9)
    if rest_w or rest_l:
        return 'rest'
    #log out and retry
    return 'logout'

def click(position):
    py.click(position)

def random_sleep(n):
    '''random sleep for try again'''
    if n == 1:
        return random.randint(35,40)
    elif n == 2:
        return random.randint(1,10)
    elif n == 3:
        return random.randint(30,180)
    else:
        return random.randint(35,40)    #in case it does not get 1,2or3 as input

def match_q(pos):
    #first look for existing screenshot to see if it knows the right answer
    global qalist,hash_cache
    exist = False
    new_screenshot = py.screenshot(region=(897,387,8,100))
    pichash = hashlib.md5(new_screenshot.tobytes())
    pichash = pichash.hexdigest()
    if hash_cache == pichash:
        print('screen frozen, refreshing')  #either screen freezes or the mouse doesn't click on any choice
        py.click(1319,43)       #refresh page
        time.sleep(5)
    else:
        for i in qalist:
            if i[0] == pichash:
                test_pos = i[1]
                if test_pos:
                    print('existing q found')
                    pos = test_pos
                    exist = True
                    break
                #else:
                #    qalist.remove(i)
                #    print('!removing existing unanswered q!')

        #click position, if the screen does not match with existing screenshots, then randomly select a choice
        click(pos)
        hash_cache = pichash
        if exist:   #record for wrong answer
            x,y = pos
            img = py.screenshot(region=(868,y-1,2,2))
            green = (16,179,4)
            c = img.getpixel((1,1))
            if c != green:
                print('!the answer is probably wrong!')
        if not exist:      #recognizing green or red area
            x,y = pos
            img = py.screenshot(region=(x-1,y-1,2,2))
            green = (16,179,4)
            c = img.getpixel((1,1))
            if c == green:
                x = int(x)      #Object of type int64 is not JSON serializable
                y = int(y)
                qalist.append([pichash,(x,y)])
                print('new q memorized, answered right')
            else:
                loc = py.locateOnScreen(r'red.png',region=(868,440,150,600))
                if loc:
                    pos = py.center(loc)
                    x,y = pos
                    x = int(x)      #Object of type int64 is not JSON serializable
                    y = int(y)
                    qalist.append([pichash,(x,y)])
                    print('new q memorized, answered wrong')
                else:
                    print('new q NOT memorized!')
            with open(r'q_a_list.json','w') as f:
                json.dump(qalist,f)

def tryagain_how_to(pos,rounds,sleep_config):
    '''things to do with after the try again sign detected: continue, rest, or logout'''
    print('盘数 {}'.format(rounds))
    sleep_time = random_sleep(sleep_config)
    print('sleeping {}s'.format(sleep_time))
    time.sleep(sleep_time)
    if rounds%31 == 0:    #sleep for 10mins
        x,y = pos
        pos = (x,y+100)
        click(pos)
        print('sleeping 620s...')
        time.sleep(5)
        time.sleep(620)
        py.click(1319,43)       #refresh page
        time.sleep(5)
    else:
        ind = rest()
        if ind == 'continue':
            click(pos)
        elif ind == 'rest':
            x,y = pos
            pos = (x,y+100)
            click(pos)
            print(datetime.now())
            print('sleeping 2h15min...')
            time.sleep(8100)        #sleep for 2.25 hours
            py.click(1319,43)       #refresh page
            time.sleep(5)
            rounds = 0
        elif ind == 'logout':
            x,y = pos
            pos = (x,y+100)
            click(pos)
            print('unknown error, refresh and retry')
            py.click(1319,43)       #refresh page
            time.sleep(5)

def control_program():
    while True:
        global sleep_config
        a = input('1 for 35-40s, 2 for 1-10s, 3 for 30s-3min, 0 for end: ')
        if a in ['1','2','3','0']:
            sleep_config = int(a)
            if sleep_config == 0:
                global running
                running = False
                sys.exit()

running = True
thread = threading.Thread(target=control_program,)
thread.start()

sleep_config = 2
rounds = 0
hash_cache = None       #if the q is the same between last click and current click, then the screen is frozen
l = [0,0,120,120,220]       #used for randomize choice being clicked
#loading q to a list
with open(r'q_a_list.json') as f:
    qalist = json.load(f)

start = time.time()

while running:
    #detect for bracket first
    pos = look_for_bracket(l)
    if pos:
        #random interval
        m = random.uniform(1.5,5)
        m = round(m,2)
        match_q(pos)
        time.sleep(m)
    #detect for tryagain
    else:
        pos = look_for_tryagain()
        if pos:
            rounds += 1
            tryagain_how_to(pos,rounds,sleep_config)
    #detect for begin
        else:
            pos = look_for_begin()
            if pos:
                print('盘数 {},自动单击开始答题'.format(rounds))
                click(pos)
    #nothing detected
            else:
                time.sleep(1)
                end = time.time()
                print('截止到目前总秒数 {} s'.format(round(end-start,1)))
                print('doing nothing')
