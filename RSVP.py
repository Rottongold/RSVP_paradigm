from __future__ import absolute_import, division
from psychopy import locale_setup, visual, core, event
from psychopy import sound
import numpy as np
import pylsl
from random import shuffle, choice
import pandas as pd
import os

win = None # Global variable for window 
bg_color = [0, 0, 0]
win_w = 1920#1920# Home monitor: 2560
win_h = 1080#1080# Home Monitor: 1440
refresh_rate = 144. # Monitor refresh rate (CRITICAL FOR TIMING)

#----------------------------------Define Helper Function--------------------------------------------
def MsToFrames(ms, fs):
    dt = 1000 / fs
    return np.round(ms / dt).astype(int)

# ---------------------------------Initialize lsl ---------------------------------------------------
info = pylsl.StreamInfo(name='speech_pilot', type='Markers', channel_count=1,
                      channel_format=pylsl.cf_string, source_id='example_stream_001')
outlet = pylsl.StreamOutlet(info)

# ---------------------------------Initialize variables----------------------------------------------- 
win = visual.Window( 
        screen = 0,
        size=[win_w, win_h], 
        fullscr= False,
        color=[0, 0, 0],
        gammaErrorPolicy = "ignore"
    )

#Sample puns since the stimulus set is still under validation process
puns = [
    'I told the carpenter not to carpet my steps. He gave me a blank stair',
    'Those who work on reducing auto emissions go home exhausted',
    'For a great vacation, put the kids in the back seat, and take a cruise',
    'If you have bladder problems. Urine challenges',
    'I got a car for my wife, and I thought it was a good trade'
]

comp_q = [
    'The sentence suggests that the carpenter gave the speaker a confused or emotionless look',
    'The sentence implies that people working on reducing auto emissions physically remove car exhaust from the air',
    '"Take a cruise" in this pun could imply both driving a car and going on a luxury cruise',
    '"Urine challenges" in this sentence refers to medical problems related to the bladder',
    'The phrase "good trade" suggests that the speaker values the car more than the wife'
]

keys = [
    't',
    'f', 
    't',
    't',
    't'
]

processed_puns = [pun.split(' ') for pun in puns]

stimulus_list = []

for i in np.arange(len(puns)):
    temp_dict = {}
    temp_dict['pun'] =  processed_puns[i]
    temp_dict['qs'] = comp_q[i]
    temp_dict['key'] = keys[i]
    
    stimulus_list.append(temp_dict)

shuffle(stimulus_list)

fixation = visual.TextStim(win, "+", font='Open Sans', units='pix', 
                pos=(0,0), alignText='center',
                height=80, color=[1, 1, 1]
                )

Instruction = visual.TextBox2(win, "In the following session, a series of sentences will be presented. For each sentence, the words will appear at the center of the screen one by one. Please stay focus at the sentences as the sentences will be followed by a comprehension question. Each comprehension question would be a T/F question. If you think it is a true statement, press T. If you think it is a false statment, press F. Please ask the experimenter now if you have any questions. \n\n  Press space to start the experiment",
            font='Open Sans', units='pix', letterHeight = 30, alignment = 'center',
pos=(0,100),color=[1, 1, 1]
)

stim_text = visual.TextStim(win, text='', font='Open Sans', units='pix', 
                pos=(0,0), alignText='center',
                height=80, color=[1, 1, 1])

temp_q = visual.TextStim(win, text='', font='Open Sans', units='pix', 
                pos=(0,0), alignText='center',
                height=70, color=[1, 1, 1], wrapWidth = 1000)

# ---------------------------------------Instruction---------------------------------------------
outlet.push_sample(pylsl.vectorstr(['Instruction']))
while True:
    Instruction.draw()
    win.flip()
    
    keys = event.getKeys()
    if 'space' in keys:
        break
    elif 'escape' in keys:
        core.quit()

# ----------------------------- Experiment ----------------------------------------

for stimuli in stimulus_list:

    stim = stimuli['pun']
    comp = stimuli['qs']
    key = stimuli['key']

    outlet.push_sample(pylsl.vectorstr(['Fixation']))
    
    # 500ms of fixation cross before the stimulus
    for i in range(MsToFrames(500, refresh_rate)):
        fixation.draw()
        win.flip()

    #RVSP paradigm, each word presented for 200 ms followed by ISI = 200 ms
    for i in range(len(stim)):

        outlet.push_sample(pylsl.vectorstr(['Trial']))

        if i == (len(stim) - 1):
             outlet.push_sample(pylsl.vectorstr(['Critical Word']))
        
        stim_text.text = stim[i]
        
        # Text presentation
        for i in range(MsToFrames(200, refresh_rate)):
            stim_text.draw()
            win.flip()

        # ISI
        for i in range(MsToFrames(200, refresh_rate)):
            fixation.draw()
            win.flip()

    # 2500ms of fixation cross (or like a pause) before the comprehension question 
    for i in range(MsToFrames(2500, refresh_rate)):
        fixation.draw()
        win.flip()

    temp_q.text = comp

    outlet.push_sample(pylsl.vectorstr(['Comp_Q']))
    
    while True:
        temp_q.draw()
        win.flip()

        resp = event.getKeys()
        
        if resp:  
            if 'escape' in resp:
                core.quit()
            
            if key in resp:
                outlet.push_sample(pylsl.vectorstr(['T']))
                break
            elif key not in resp:
                outlet.push_sample(pylsl.vectorstr(['F']))
                break


## make sure everything is closed down
#win.close()
#core.quit()

    
