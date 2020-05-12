#!/bin/bash

####### ~/.bin/controlvlc_socket.sh
#
# Purpose:      Control vlc using your multimedia keys or cli
# Author:       j@mesrobertson.com
# Date:         11-03-2011
# Dependancies: netcat-openbsd
#
# Instructions: 
#
#   * Place this scipt in your path and make it executable.
#   * Open VLC.
#   * Go to Tools > Preferences and change "Show Settings" to "All".
#   * Drill down to "Interface" > "Main Inteface" and select "Remote
#     control interace".
#   * Drill down from "Main Interface" to RC and select "Fake TTY" and in
#     "UNIX socket command input" type in:  /tmp/vlc.sock
#   * Click Save.
#   * Restart VLC.
#   * Bind a shortcut key in you WM or DE for each command e.g. in
#     Openbox rc.xml's "keyboard" section and example is:
#
#   ...
#   <keybind key="XF86AudioPlay">
#      <action name="Execute">
#         <execute>controlvlc_socket.sh pause</execute>
#      </action>
#   </keybind>
#   ...
#
#   you can of course execute these straight from the cli to test.
#   type "controlvlc_socket.sh help" for details about the
#   available commands.
#
#   It is up to your imagination how you bind any other commands that
#   you would like to use.  I imagine some Conky goodness :)
#
#######


vlcSocket="tmp/vlc.sock"

case $1 in

        add)            command="add" ;; 
        enqueue)        command="enqueue" ;; 
        playlist)       command="playlist" ;; 
        search)         command="search" ;; 
        sort)           command="sort" ;; 
        sd)             command="sd" ;; 
        play)           command="play" ;; 
        stop)           command="stop" ;; 
        next)           command="next" ;; 
        prev)           command="prev" ;; 
        goto)           command="goto" ;; 
        repeat)         command="repeat" ;; 
        loop)           command="loop" ;; 
        random)         command="random" ;; 
        clear)          command="clear" ;; 
        status)         command="status" ;; 
        title)          command="title" ;; 
        title_n)        command="title_n" ;; 
        title_p)        command="title_p" ;; 
        chapter)        command="chapter" ;; 
        chapter_n)      command="chapter_n" ;; 
        chapter_p)      command="chapter_p" ;; 
        seek)           command="seek" ;; 
        pause)          command="pause" ;; 
        fastforward)    command="fastforward" ;; 
        rewind)         command="rewind" ;; 
        faster)         command="faster" ;; 
        slower)         command="slower" ;; 
        normal)         command="normal" ;; 
        rate)           command="rate" ;; 
        frame)          command="frame" ;; 
        fullscreen)     command="fullscreen" ;; 
        info)           command="info" ;; 
        stats)          command="stats" ;; 
        get_time)       command="get_time" ;; 
        is_playing)     command="is_playing" ;; 
        get_title)      command="get_title" ;; 
        get_length)     command="get_length" ;; 
        volume)         command="volume" ;; 
        volup)          command="volup" ;; 
        voldown)        command="voldown" ;; 
        adev)           command="adev" ;; 
        achan)          command="achan" ;; 
        atrack)         command="atrack" ;; 
        vtrack)         command="vtrack" ;; 
        vratio)         command="vratio" ;; 
        vcrop)          command="vcrop" ;; 
        vzoom)          command="vzoom" ;; 
        snapshot)       command="snapshot" ;; 
        strack)         command="strack" ;; 
        hotkey)         command="hotkey" ;; 
        menu)           command="menu" ;; 
        set)            command="set" ;; 
        save_env)       command="save_env" ;; 
        alias)          command="alias" ;; 
        description)    command="description" ;; 
        license)        command="license" ;; 
        help)           command="help" ;; 
        longhelp)       command="longhelp" ;; 
        logout)         command="logout" ;; 
        quit)           command="quit" ;; 
        shutdown)       command="shutdown" ;;
        *)              echo "$0: unknown parameter '$1' ;;

esac

exec echo "$1" | nc -UN ${vlcSocket}


####### END #######
