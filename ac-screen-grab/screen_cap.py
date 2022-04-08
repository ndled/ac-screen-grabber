#!/usr/bin/env python3
import argparse
import logging
import os
import pdb
import sys
import traceback
import typing
from collections.abc import Callable
import math
import random

import cv2

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def idb_excepthook(type, value, tb):
    """Call an interactive debugger in post-mortem mode

    If you do "sys.excepthook = idb_excepthook", then an interactive debugger
    will be spawned at an unhandled exception
    """
    if hasattr(sys, "ps1") or not sys.stderr.isatty():
        sys.__excepthook__(type, value, tb)
    else:
        traceback.print_exception(type, value, tb)
        print
        pdb.pm()


def resolvepath(path):
    return os.path.realpath(os.path.normpath(os.path.expanduser(path)))


def parseargs(arguments: typing.List[str]):
    """Parse program arguments"""
    parser = argparse.ArgumentParser(description="Python command line script template")
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Launch a debugger on unhandled exception",
    )
    parser.add_argument(
        "--video_dir",
        "-v",
        action="store",
        help="Video directory to cut up into frames",
    )
    parsed = parser.parse_args(arguments)
    return parsed


def broken_pipe_handler(
    func: Callable[[typing.List[str], int]], *arguments: typing.List[str]
) -> int:
    """Handler for broken pipes

    Wrap the main() function in this to properly handle broken pipes
    without a giant nastsy backtrace.
    The EPIPE signal is sent if you run e.g. `script.py | head`.
    Wrapping the main function with this one exits cleanly if that happens.

    See <https://docs.python.org/3/library/signal.html#note-on-sigpipe>
    """
    try:
        returncode = func(*arguments)
        sys.stdout.flush()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        # Convention is 128 + whatever the return code would otherwise be
        returncode = 128 + 1
    return returncode


def make_dirs():
    if not os.path.exists('assets/imgs'):
        os.makedirs(resolvepath('assets/imgs'))

def video_cut(video_path):
    count = 0
    image_name = os.path.basename(video_path)
    cap = cv2.VideoCapture(video_path)
    frameRate = cap.get(5)
    while(cap.isOpened()):
        frameId = cap.get(1)
        ret, frame = cap.read()
        if (ret != True):
            break
        if (frameId % math.floor(frameRate)*60 == 0):
            name =image_name + str(count).zfill(5) + ".jpg";count+=1
            cv2.imwrite(resolvepath(f"assets/imgs/{name}"), frame)
        print("working on " + str(count), end='\r')
    cap.release()
    print("")
    print ("Done!")

def single_cut():
    for file in os.listdir(resolvepath("static/single")):
        video_path = resolvepath(f"static/single/{file}")
    image_name = os.path.basename(video_path)
    cap = cv2.VideoCapture(video_path)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    randomframe = random.randint(0,length)
    while(cap.isOpened()):
        frameId = int(cap.get(1))
        print(frameId)
        ret, frame = cap.read()
        if (ret != True):
            break
        if (frameId == randomframe):
            cv2.imwrite(resolvepath(f"static/single/{image_name}.jpg"), frame)
            image_path = f"static/single/{image_name}.jpg"
            print("wrote")
            cap.release()
            return image_path
    cap.release()

def new_cut(path):
    for file in os.listdir(resolvepath(path)):
        video_path = resolvepath(f"{path}/{file}")
    count = 0
    image_name = os.path.basename(video_path)
    cap = cv2.VideoCapture(video_path)
    frameRate = cap.get(5)
    while(cap.isOpened()):
        frameId = cap.get(1)
        ret, frame = cap.read()
        if (ret != True):
            break
        if (frameId % math.floor(frameRate)*60 == 0):
            name =image_name + str(count).zfill(5) + ".jpg";count+=1
            cv2.imwrite(resolvepath(f"static/new/{name}"), frame)
        print("working on " + str(count), end='\r')
    cap.release()
    print("")
    print ("Done!")

def mass_cut(video_dir):
    if os.path.exists(resolvepath(f"tmp/video_list.txt")):
        with open(resolvepath(f"tmp/video_list.txt"), 'r') as f:
            lines = f.read()
            video_list = lines.splitlines()
    else:
        video_list = []
    for video in os.listdir(video_dir):
        if video not in video_list:
            video_cut(resolvepath(f"tmp/videos/{video}"))
            with open(resolvepath(f"tmp/video_list.txt"),'a') as vid_file:
                vid_file.write(video)

def main(*arguments):
    """Main program"""
    parsed = parseargs(arguments[1:])
    if parsed.debug:
        sys.excepthook = idb_excepthook
    make_dirs()
    mass_cut(parsed.video_dir)



if __name__ == "__main__":
    exitcode = broken_pipe_handler(main, *sys.argv)
    sys.exit(exitcode)