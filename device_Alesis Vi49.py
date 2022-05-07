# name=Alesis Vi49

import transport
import channels

CHANNEL_SELECT = 0
PICKUP_THRESH = 0.08
BIT_SCALER_127_TO_1 = 0.0078740157481
BIT_SCALER_63_TO_1 = 0.0158730158731
BIT_SCALER_64_TO_1 = 0.015625


#   CC: Switch No. (start from 0)
altLut = {
    20: 0,      # SWITCH 01     
    21: 1,      # SWITCH 02
    50: 2,      # SWITCH 03   
    51: 3,      # SWITCH 04   
    52: 4,      # SWITCH 05   
    53: 5,      # SWITCH 06   
    54: 6,      # SWITCH 07   
    55: 7,      # SWITCH 08   
    56: 8,      # SWITCH 09   
    57: 9,      # SWITCH 10   
    58: 10,     # SWITCH 11  
    59: 11,     # SWITCH 12  
    64: 12,     # SWITCH 13  
    65: 13,     # SWITCH 14  
    66: 14,     # SWITCH 15  
    67: 15,     # SWITCH 16  
    68: 16,     # SWITCH 17  
    69: 17,     # SWITCH 18  
    70: 18,     # SWITCH 19  
    71: 19,     # SWITCH 20  
    72: 20,     # SWITCH 21  
    73: 21,     # SWITCH 22  
    74: 22,     # SWITCH 23  
    75: 23,     # SWITCH 24  
    80: 24,     # SWITCH 25  
    81: 25,     # SWITCH 26  
    82: 26,     # SWITCH 27  
    83: 27,     # SWITCH 28  
    84: 28,     # SWITCH 29  
    85: 29,     # SWITCH 30
    86: 30,     # SWITCH 31  
    87: 31,     # SWITCH 32  
    88: 32,     # SWITCH 33  
    89: 33,     # SWITCH 34  
    90: 34,     # SWITCH 35  
    91: 35,     # SWITCH 36      
}

#   CC: Rotary No. (start from 0)
rotary_table = {
    14: 0,      # ROTARY 1
    76: 1       # ROTARY 2
}

#   CC: Function
functionalButtons = {
    "RECORD": 3,
    "LOOP": 9,
    "PLAY": 22,
    "STOP": 23,
    "FAST_FORWARD": 24,
    "REWIND": 25
}

def rotaryDialConversion(eventVelocity):
    panAmount = 0

    # Lower Half, 63 down to 0 CONVERT TO -63 up to 0 i.e -1 to 0
    if eventVelocity <= 63:
        panAmount = ((63 - eventVelocity) * -1) * BIT_SCALER_63_TO_1

    # Upper Half, 63 up to 127 CONVERT TO 0 up to 64 i.e 0 to 1
    elif eventVelocity > 63:
        panAmount = (eventVelocity - 63) * BIT_SCALER_64_TO_1 

    return panAmount


def OnMidiMsg(event):
    global CHANNEL_SELECT

    event.handled = False
    # Enable Tp debug
    # print(event.midiId, event.data1, event.data2, event.velocity, "Button Pressed")
    # print("CC=",event.data1)

    # Handle Functional Buttons
    if (event.data1 in functionalButtons.values()):
        # print(transport.isPlaying())
        # print(event.data1)
        if functionalButtons["RECORD"] == event.data1:
            transport.record()
        if functionalButtons["LOOP"] == event.data1:
            transport.setLoopMode()
        if functionalButtons["PLAY"] == event.data1:
            transport.start()
        if functionalButtons["STOP"] == event.data1:
            transport.stop()
        if functionalButtons["FAST_FORWARD"] == event.data1:
            if event.velocity == 127:
                transport.fastForward(2)
            elif event.velocity == 0:
                transport.fastForward(0)
        if functionalButtons["REWIND"] == event.data1:
            if event.velocity == 127:
                transport.rewind(2)
            elif event.velocity == 0:
                transport.rewind(0)
               

    padOffset = 102                             # Where CC starts for the drum pads
    numberOfPads = 16
    padToChannel = event.data1 - padOffset

    if (event.midiId == 176 and event.velocity == 127 and event.data1 in altLut):
        channelSelectBySwitch = altLut[event.data1]
        CHANNEL_SELECT = channelSelectBySwitch
        # print(f"Channel SELECTED: {channelSelectBySwitch} ----------- CC: {event.data1}, Switch Toggeled: {channelSelectBySwitch+1}")

    if (event.midiId == 176 and event.velocity == 0 and event.data1 in altLut):
        channelSelectBySwitch = altLut[event.data1]
        CHANNEL_SELECT = 0  # RESET - See if it can deselect
        # print(f"Channel DE-SELECTED: {channelSelectBySwitch} ----------- CC: {event.data1}, Switch Toggeled: {channelSelectBySwitch+1}")
        # Remove channel when finished

    # Control Volume - CC 14 in the rotary table - It might be better to change them to use the switch/rotor number as a key instead.
    # Todo change this to look 
    if event.midiId == 176 and event.data1 == 14:
        currentChannelVelocity = channels.getChannelVolume(CHANNEL_SELECT)
        rotaryVelocity = event.velocity * BIT_SCALER_127_TO_1

        if rotaryVelocity < currentChannelVelocity + PICKUP_THRESH and rotaryVelocity > currentChannelVelocity - PICKUP_THRESH :
            channels.setChannelVolume(CHANNEL_SELECT, rotaryVelocity, 1)

    # Control Pan - CC 76
    if event.midiId == 176 and event.data1 == 76:
        currentChannelPan = channels.getChannelPan(CHANNEL_SELECT)
        rotaryPan = rotaryDialConversion(event.velocity)

        if rotaryPan < currentChannelPan + PICKUP_THRESH and rotaryPan > currentChannelPan - PICKUP_THRESH :
            channels.setChannelPan(CHANNEL_SELECT, rotaryPan, 1)


    # Note 36 is middle C
    if (event.midiId == 176 and event.velocity == 127 and event.data1 >= padOffset and event.data1 < padOffset + numberOfPads):
        try:
            channels.midiNoteOn(padToChannel, 60, 100)
            print(f"PAD{padToChannel + 1}")
        except (TypeError):
            print(f"INVALID CHANNEL: {padToChannel + 1}")

    if (event.midiId == 176 and event.velocity == 0 and event.data1 >= padOffset and event.data1 < padOffset + numberOfPads):
        try:
            channels.midiNoteOn(padToChannel, 60, 0)
            print(f"PAD{padToChannel + 1}")
        except (TypeError):
            print(f"Here INVALID CHANNEL: {padToChannel + 1}" )

# Todo map some more rotaries