#!/usr/bin/python

import sys,os,time, random
from optparse import OptionParser
from gm_termcontrol.termcontrol import termcontrol, pyteLogger, boxDraw, widget, widgetScreen
from gm_termcontrol.termcontrol import widgetProgressBar, widgetSlider, widgetButton
from gm_pymms.pymms import pymms
from gm_pymms.interface import interface_ansi

def main():
    parser=OptionParser(usage="usage: %prog [options] AUDIO_FILES")
    parser.add_option("-p", "--play", action='store_true', dest="play",
            default=False, help="Play immediately.")
    parser.add_option("-r", "--record", action='store_true', dest="record",
            default=False, help="Record mode.")
    parser.add_option("-i", "--interface", default='auto', dest="interface",
            help="Select the interface: auto | ansi | kitty | X")
    parser.add_option("-S", "--shuffle", action='store_true', dest="shuffle",
            default=False, help="Turn on shuffle.")
    parser.add_option("-R", "--repeat", action='store_true', dest="repeat",
            default=False, help="Turn on repeat.")
    parser.add_option("-L", "--list", action='store_true', dest="playlist",
            default=False, help="show playlist.")
    parser.add_option("-v", "--verbose", dest="debug", default="info",
            help="Show debug messages.[debug, info, warning]")
    parser.add_option("-s", dest="script", default="No script was given.",
            help="Script for record mode.")
    parser.add_option("-x", dest="x", default=1, help="Left coordinate.")
    parser.add_option("-y", dest="y", default=1, help="Top coordinate.")
    (options, args)=parser.parse_args()
    if len(args)==0:
        parser.print_help()
        return
    mode='play'
    if options.record:
        mode='record'
    
    if options.interface.lower() == 'auto':
        options.interface='ansi'

    if options.interface.lower() == 'ansi':
        tp=interface_ansi(x=int(options.x), y=int(options.y), mode=mode,
                      script=options.script, files=args,
                      shuffle=options.shuffle, repeat=options.repeat,
                      play=options.play,
                      playlist=options.playlist and not options.record)
        tp.kb.disable_keyboard_echo()
        print(tp.t.disable_cursor(), end='')
        print(tp.t.disable_mouse(), end='')
        tp.guiLoop()
        tp.kb.enable_keyboard_echo()
        print(tp.t.enable_cursor(), end='')
        print(tp.t.enable_mouse(), end='')
    if options.interface.lower() == 'kitty':
        pass
    if options.interface.lower() == 'x':
        pass
    return

if __name__ == "__main__":
    main()
