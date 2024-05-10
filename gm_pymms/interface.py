#!/usr/bin/python

import sys, os, time, random, zipfile
from gm_termcontrol.termcontrol import termcontrol, pyteLogger, boxDraw, widget, widgetScreen
from gm_termcontrol.termcontrol import widgetProgressBar, widgetSlider, widgetButton
from gm_pymms.pymms import pymms
try:
    from PIL import ImagXe
except ImportError:
    sys.stderr.write("You need to install PIL module!\n"
                     "Defaulting to ansi terminal interface\n")

"""
         0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
U+250x   ─   ━   │   ┃   ┄   ┅   ┆   ┇   ┈   ┉   ┊   ┋   ┌   ┍   ┎   ┏
U+251x   ┐   ┑   ┒   ┓   └   ┕   ┖   ┗   ┘   ┙   ┚   ┛   ├   ┝   ┞   ┟
U+252x   ┠   ┡   ┢   ┣   ┤   ┥   ┦   ┧   ┨   ┩   ┪   ┫   ┬   ┭   ┮   ┯
U+253x   ┰   ┱   ┲   ┳   ┴   ┵   ┶   ┷   ┸   ┹   ┺   ┻   ┼   ┽   ┾   ┿
U+254x   ╀   ╁   ╂   ╃   ╄   ╅   ╆   ╇   ╈   ╉   ╊   ╋   ╌   ╍   ╎   ╏
U+255x   ═   ║   ╒   ╓   ╔   ╕   ╖   ╗   ╘   ╙   ╚   ╛   ╜   ╝   ╞   ╟
U+256x   ╠   ╡   ╢   ╣   ╤   ╥   ╦   ╧   ╨   ╩   ╪   ╫   ╬   ╭   ╮   ╯
U+257x   ╰   ╱   ╲   ╳   ╴   ╵   ╶   ╷   ╸   ╹   ╺   ╻   ╼   ╽   ╾   ╿
U+258x   ▀   ▁   ▂   ▃   ▄   ▅   ▆   ▇   █   ▉   ▊   ▋   ▌   ▍   ▎   ▏
U+259x   ▐   ░   ▒   ▓   ▔   ▕   ▖   ▗   ▘   ▙   ▚   ▛   ▜   ▝   ▞   ▟
U+25Ax   ■   □   ▢   ▣   ▤   ▥   ▦   ▧   ▨   ▩   ▪   ▫   ▬   ▭   ▮   ▯
U+25Bx   ▰   ▱   ▲   △   ▴   ▵   ▶   ▷   ▸   ▹   ►   ▻   ▼   ▽   ▾   ▿
U+25Cx   ◀   ◁   ◂   ◃   ◄   ◅   ◆   ◇   ◈   ◉   ◊   ○   ◌   ◍   ◎   ●
U+25Dx   ◐   ◑   ◒   ◓   ◔   ◕   ◖   ◗   ◘   ◙   ◚   ◛   ◜   ◝   ◞   ◟
U+25Ex   ◠   ◡   ◢   ◣   ◤   ◥   ◦   ◧   ◨   ◩   ◪   ◫   ◬   ◭   ◮   ◯
U+25Fx   ◰   ◱   ◲   ◳   ◴   ◵   ◶   ◷   ◸   ◹   ◺   ◻   ◼   ◽  ◾  ◿
"""

STOP=0
PLAY=1
RECORD=2

class interface():
    def __init__(self, mode='play', files=[], script="",
                 repeat=False, shuffle=False, play=False, playlist=False):
        self.go=False
        self.showPlayList=False
        self.clearPlayList=False
        self.playlist=files
        self.playlistinorder=files.copy()
        self.playListInfo={}
        self.repeat=repeat
        self.playlistbuffer=''
        self.playerbuffer=''
        if shuffle:
            self.shuffle()
        self.mode=mode
        for f in files:
            self.playListInfo[f]=self.mediaInfo(f)
        if self.mode=='record':
            if len(self.playlist)!=1:
                print("Record mode must reference one audio filename.")
                exit(1)
        else:
            pass
        self.filename=files[0]
        self.player=pymms()
        self.player.au.endHandler=self.endHandler
        if self.mode=='play':
            self.load(self.filename)
        self.script=script
        if play: self.play()
        if playlist: self.togglePlayList()

    def minsec(self, s):
        s=int(s)
        mins=int(s/60)
        secs=int(s%60)
        return f'{mins:02d}:{secs:02d}'

    def scroll_string(self, str, max_length, clock=0):
        max_index=len(str)-max_length
        if max_index>0:
            cl=0
            cl=int(clock)%(2*max_index)
            rv=0
            if cl>max_index:
                rv=cl-max_index
            st=int(cl-2*rv)
            return str[st:st+max_length]
        return str

    def mediaInfo(self, f): #generic
        title=os.path.basename(f)
        length=0
        bitrate=0
        quality=0
        channels=1
        info={'title':title, 'length':length, 'bitrate':bitrate, 'quality':quality, 'channels':channels}
        self.playListInfo[f]=info
        return info

    def togglePlayList(self):   #generic
        self.showPlayList=not self.showPlayList
        self.playlistbuffer=''
        if not self.showPlayList:
            self.clearPlayList=True

    def load(self, filename):    #generic:
        info=self.player.load(filename)
        self.playListInfo[filename]=info
        self.filename=filename

    def save(self, filename):
        self.player.save(filename)#generic

    def quit(self): #generic
        if self.mode=='record':
            #TODO save prompt
            if(1):
                self.save(self.filename)
        self.stop()
        if self.go:
            self.go=False
        else:
            pass
            #quit()

    def next(self):
        i=self.playlist.index(self.filename)
        i+=1
        if i>=len(self.playlist):
            i=0
        p=self.player.au.status
        self.load(self.playlist[i])
        if p==PLAY:
            self.play()

    def prev(self):
        i=self.playlist.index(self.filename)
        i-=1
        if i<0:
            i=len(self.playlist)-1
        p=self.player.au.status
        self.load(self.playlist[i])
        if p==PLAY:
            self.play()

    def endHandler(self):
        if self.player.au.status==PLAY:
            if self.mode=='play':
                if self.repeat:
                    self.stop()
                    self.play()
                else:
                    self.next()
            else:
                self.player.pause()

    def shuffle(self):
        if self.playlist==self.playlistinorder:
            random.shuffle(self.playlist)
        else:
            self.playlist=self.playlistinorder.copy()

    def repeat(self):
        self.repeat = not self.repeat

    def seek(self, pos=0):
        self.player.seek_time(pos)

    def seekFwd(self):
        self.player.seekFwd_time(10)

    def seekBack(self):
        self.player.seekBack_time(10)

    def eject(self):
        pass

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def playpause(self):
        self.player.playpause()

    def stop(self):
        self.player.stop()

    def record(self):
        self.player.record()

    def denoise(self):
        self.player.denoise()

    def normalize(self):
        self.player.normalize()

class interface_ansi(interface, widget):
    def __init__(self, x=1, y=1, w=80, h=15, mode='play', files=[], script="",
                 repeat=False, shuffle=False, play=False, playlist=False):
        interface.__init__(self, mode=mode, files=files, script=script, repeat=repeat, 
                         shuffle=shuffle, play=play, playlist=playlist)
        self.icons={}
        self.icons['prev']     = {"label":'\u23ee',   "key":'[', 'action':self.prev}
        self.icons['prev']     = {"label":'\u25ae'+'\u25c0'*2, "key":'[', 'action':self.prev}
        self.icons['next']     = {"label":'\u23ed',   "key":']', 'action':self.next}
        self.icons['next']     = {"label":'\u25b6'*2+'\u25ae', "key":']', 'action':self.next}
        self.icons['play']     = {"label":'\u25b6',   "key":'P', 'action':self.play}
        self.icons['pause']    = {"label":'\u25ae'*2, "key":'p', 'action':self.pause}
        self.icons['play/pause']={"label":'\u25b6'+'\u25ae'*2, "key":'p', 'action':self.playpause}
        self.icons['stop']     = {"label":'\u25a0',   "key":'s', 'action':self.stop}
        self.icons['record']   = {"label":'\u25cf',   "key":'r', 'action':self.record}
        self.icons['eject']    = {"label":'\u23cf',   "key":'j', 'action':self.eject}
        self.icons['shuffle']  = {"label":'\u292e',   "key":'S', 'action':self.shuffle}
        self.icons['repeat']   = {"label":'\u21bb',   "key":'R', 'action':self.repeat}
        self.icons['seek']     = {"label":'',         "key":'k', 'action':self.seek}
        self.icons['seek-']    = {"label":'\u25c0'*2, "key":'-', 'action':self.seekBack}
        self.icons['seek+']    = {"label":'\u25b6'*2, "key":'+', 'action':self.seekFwd}
        self.icons['playlist'] = {"label":'\u2263',   "key":'L', 'action':self.togglePlayList}
        self.icons['denoise']  = {"label":'\u2593\u2592\u2591', "key":'N', 'action':self.denoise}
        self.icons['normalize']= {"label":'\u224b',   "key":'Z', 'action':self.normalize}
        self.icons['quit']=      {"label":'Quit',     "key":'q', 'action':self.quit}
        widget.__init__(self, x=x, y=y, w=w, h=h) 
        self.frame=0
        self.anim="\\-/|"
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        sh=termcontrol.get_terminal_size(0)['rows']
        self.playerbox=widgetScreen(self.x, self.y, self.w, self.h, bg=234, fg=15, style='outside')
        self.playlistbox=widgetScreen(self.x, self.y+self.h, self.w, sh-self.h, bg=234, fg=15, style='outside')
        self.addWidget(self.playerbox)
        self.addWidget(self.playlistbox)
        boxHeight=7
        timeBoxW=30
        self.timeBox=widgetScreen(2, 1, timeBoxW, boxHeight, bg=233, fg=27, style='inside')
        self.playerbox.addWidget(self.timeBox)
        self.infoBox=widgetScreen(2+timeBoxW+2, 1, self.w-4-(timeBoxW+4), boxHeight, bg=233, fg=27, style='inside')
        self.playerbox.addWidget(self.infoBox)
        self.timeBox.box.tintFrame('#555')
        self.infoBox.box.tintFrame('#555')
        self.slider=widgetSlider(2, boxHeight+1, self.w-(2*2), 0, self.player.length(), labelType='time' , key='k')
        self.playerbox.addWidget(self.slider)
        self.addButtons(mode)

    def addButtons(self,mode): #interface_ansi
        playbuttons=['prev', 'play/pause', 'stop', 'next', '', 'shuffle', 'repeat', 'playlist', '', 'quit']
        recordbuttons=['seek-', 'play/pause', 'stop', 'record', 'seek+', '', 'denoise', 'normalize', '', 'quit']
        buttons=playbuttons
        if mode=='record':
            buttons=recordbuttons
        else:
            buttons=playbuttons
        self.btn={}
        btnX=2
        btnY=10
        btnW=7
        btnH=4
        x=0
        for label in buttons:
            if self.icons.get(label):
                i=self.icons[label]
                toggle=None
                if label in ['shuffle', 'playlist', 'repeat']:
                    if label=='shuffle':
                        toggle=not (self.playlist==self.playlistinorder)
                    if label=='playlist':
                        toggle=self.showPlayList
                    if label=='repeat':
                        toggle=self.repeat
                self.btn[label]=widgetButton(x*btnW+btnX, btnY, btnW, btnH, fg=27, bg=233, caption=i['label'], key=i['key'], action=i['action'], toggle=toggle)
                self.playerbox.addWidget(self.btn[label])
            x+=1

    def drawBigString(self, s): #interface_ansi
        chars={}
        chars['Resolution']='5x4'
        chars['0']= " ▄▄  "\
                    "█  █ "\
                    "▄  ▄ "\
                    "▀▄▄▀ "
        chars['1']= "     "\
                    "   █ "\
                    "   ▄ "\
                    "   ▀ "
        chars['2']= " ▄▄  "\
                    "   █ "\
                    "▄▀▀  "\
                    "▀▄▄  "
        chars['3']= " ▄▄  "\
                    "   █ "\
                    " ▀▀▄ "\
                    " ▄▄▀ "
        chars['4']= "     "\
                    "█  █ "\
                    " ▀▀▄ "\
                    "   ▀ "
        chars['5']= " ▄▄  "\
                    "█    "\
                    " ▀▀▄ "\
                    " ▄▄▀ "
        chars['6']= " ▄▄  "\
                    "█    "\
                    "▄▀▀▄ "\
                    "▀▄▄▀ "
        chars['7']= " ▄▄  "\
                    "   █ "\
                    "   ▄ "\
                    "   ▀ "
        chars['8']= " ▄▄  "\
                    "█  █ "\
                    "▄▀▀▄ "\
                    "▀▄▄▀ "
        chars['9']= " ▄▄  "\
                    "█  █ "\
                    " ▀▀▄ "\
                    " ▄▄▀ "
        chars[':']= "     "\
                    "  ●  "\
                    "  ●  "\
                    "     "
        chars[' ']= "     "\
                    "     "\
                    "     "\
                    "     "
        col,row=chars['Resolution'].split('x')
        col=int(col)
        row=int(row)
        buffer=""
        for y in range(row):
            for c in s:
                fc=chars.get(c)
                if fc:
                    buffer+=fc[y*col:(y+1)*col]
                else:
                    buffer+=" "
            buffer+='\n'
        return buffer

    def drawMultiLine(self, x, y, s):   #interface_ansi
        lines=s.split('\n')
        dy=0
        buffer=""
        for l in lines:
            buffer+=self.t.gotoxy(x, y+dy)
            buffer+=l
            dy=dy+1
        return buffer

    def draw(self): #interface_ansi
        t=self.player.get_cursor_time()
        self.slider.setValue(t)
        self.slider.setMax(max(self.player.length_time(), t))
        timestr=self.drawBigString(self.minsec(t))
        buffer=''
        fg=27
        if self.player.au.status==RECORD:
            fg=196
        else:
            fg=27
        if self.mode=='record':
            self.infoBox.feed(self.t.clear())
            self.infoBox.feed(self.t.gotoxy(1, 1))
            self.infoBox.feed(self.t.ansicolor(27))
            self.infoBox.feed(self.script)
        elif self.mode=='play':
            self.infoBox.feed(self.t.clear())
            self.infoBox.feed(self.t.ansicolor(27))
            title=""
            title=f'{self.playlist.index(self.filename)+1}. '
            if self.playListInfo[self.filename]:
                title+=self.playListInfo[self.filename]['title']
                title+=f' ({self.minsec(self.playListInfo[self.filename]["length"])})'
            self.infoBox.feed(self.t.gotoxy(1, 1))
            self.infoBox.feed(self.scroll_string(title, 38, clock=t))
            quality=0
            bitrate=0
            channels=0
            if self.playListInfo[self.filename]:
                quality=int(self.playListInfo[self.filename]["quality"])
                bitrate=int(self.playListInfo[self.filename]["bitrate"])
                channels=int(self.playListInfo[self.filename]["channels"])
            self.infoBox.feed(self.t.gotoxy(1, 3))
            self.infoBox.feed(f'{int(quality)}kbps')
            self.infoBox.feed(self.t.gotoxy(14, 3))
            self.infoBox.feed(f'{bitrate}kHz')
            self.infoBox.feed(self.t.gotoxy(31, 3))
            if channels==0:
                self.infoBox.feed(f'No Audio')
            elif channels==1:
                self.infoBox.feed(f'    Mono')
            elif channels==2:
                self.infoBox.feed(f'  Stereo')
            else:
                self.infoBox.feed(f' Stereo+')
        self.timeBox.feed(self.t.ansicolor(fg,233, bold=True))
        self.timeBox.feed(self.t.clear())
        self.timeBox.feed(self.drawMultiLine(30-(5*5)-2, 1, timestr))
        self.timeBox.feed(self.t.gotoxy(1, 3))
        if self.player.au.status==PLAY:
            i=self.icons['play']
            self.timeBox.feed(self.t.ansicolor(46, 233, bold=True))
            self.timeBox.feed(i['label'])
        elif self.player.au.status==RECORD:
            i=self.icons['record']
            self.timeBox.feed(self.t.ansicolor(196, 233, bold=True))
            self.timeBox.feed(i['label'])
        elif self.player.au.status==STOP:
            i=self.icons['stop']
            self.timeBox.feed(self.t.ansicolor(27, 233, bold=True))
            self.timeBox.feed(i['label'])
        rcolor=234
        scolor=234
        if self.repeat:
            rcolor=27
        if self.playlist!=self.playlistinorder:
            scolor=27
        i=self.icons['repeat']
        self.timeBox.feed(self.t.gotoxy(1, 4))
        self.timeBox.feed(self.t.ansicolor(rcolor, 233, bold=True))
        self.timeBox.feed(i['label'])
        i=self.icons['shuffle']
        self.timeBox.feed(self.t.gotoxy(1, 5))
        self.timeBox.feed(self.t.ansicolor(scolor, 233, bold=True))
        self.timeBox.feed(i['label'])
        playerbuffer=self.playerbox.draw()
        if playerbuffer!=self.playerbuffer:
            buffer+=playerbuffer
            self.playerbuffer=playerbuffer
        if self.showPlayList:
            self.playlistbox.feed(f'{self.t.clear()}')
            startline=self.playlist.index(self.filename)
            if startline+self.playlistbox.h-3>len(self.playlist):
                startline=len(self.playlist)-(self.playlistbox.h-2)
            if startline<0:
                startline=0
            for n in range(self.playlistbox.h-2):
                color=27
                if n+startline<len(self.playlist):
                    f=self.playlist[startline+n]
                    if f==self.filename:
                        color=46
                    self.playlistbox.feed(f'{self.t.gotoxy(1,n+1)}')
                    self.playlistbox.feed(f'{self.t.ansicolor(color)}')
                    title=f
                    tm="00:00"
                    if self.playListInfo[f]:
                        title=f"{self.playListInfo[f]['title']}"
                        tm=f"{self.minsec(self.playListInfo[f]['length'])}"
                    else:
                        title=os.path.basename(title)
                    PL_line_length=self.playlistbox.w-4-len(f' {tm}')-len(f'{n+startline+1}. ')
                    self.playlistbox.feed(f'{n+startline+1}. {self.scroll_string(title, PL_line_length, clock=0)}')
                    self.playlistbox.feed(f'{self.t.gotoxy(self.playlistbox.w-3-len(tm), n+1)}')
                    self.playlistbox.feed(f'{tm}')
                else:
                    self.playlistbox.feed(f'{self.t.gotoxy(1,n+1)} ')

            playlistbuffer=self.playlistbox.draw()
            if playlistbuffer!=self.playlistbuffer:
                buffer+=playlistbuffer
                self.playlistbuffer=playlistbuffer
        else:
            if self.clearPlayList:
                self.clearPlayList=False
                buffer+=self.t.reset()
                for y in range(self.y+self.h,self.y+self.h+self.playlistbox.h):
                    buffer+=self.t.gotoxy(self.x, y)
                    for x in range(0, self.w):
                        buffer+=' '
        #print(self.anim[self.frame % len(self.anim)])
        self.frame +=1
        return buffer

class interface_kitty(interface, widget):
    def __init__(self):
        pass

class interface_x(interface, widget):
    def __init__(self):
        pass

class interface_auto(interface, widget):
    def __init__(self):
        pass

