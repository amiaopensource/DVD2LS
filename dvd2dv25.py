#!/usr/bin/env python

# Created at AMIA Hackday2015 by Dianne Dietrich, Morgan Morel, Brendan Coates, Tre Berney, and Sadie Roosa

import sys
import glob
import os
import re
from collections import defaultdict
import subprocess
from shutil import rmtree
import time

TIMEDATE = time.strftime("%Y%m%d%H%M%S")

def main():
    PathToOutput = SetupOutput(sys.argv[2])
    PathToVTS = TestISO(sys.argv[1])
    DictOfVTS = VOBDict(PathToVTS)
    ThisVOBLists = CreateVOBLists(DictOfVTS, PathToOutput)
    ffmpegConcat(ThisVOBLists, PathToOutput)
    AllConcatsPath = os.path.join(PathToOutput, 'concats', '*.VOB')
    AllConcats = glob.glob(AllConcatsPath)
    for ac in AllConcats:
        thisHeight, thisDAR = ffprobe(ac)
        createFinal(PathToOutput, ac, thisHeight, thisDAR)
    deleteWorkFiles(PathToOutput)
    print 'DONE!'

def deleteWorkFiles(OutputPath):
    #Deletes /voblist and /concats in the output folder
    rmtree(os.path.join(OutputPath, 'voblists'))
    rmtree(os.path.join(OutputPath, 'concats'))

def SetupOutput(OutputPath):
    OutputPath = os.path.expanduser(OutputPath)
    if not os.path.exists(OutputPath):
        sys.exit('Output directory does not exist.')
    else:
        try:
            os.makedirs(os.path.join(OutputPath, 'voblists'))
            os.makedirs(os.path.join(OutputPath, 'concats'))
            os.makedirs(os.path.join(OutputPath, 'final_{0}'.format(TIMEDATE)))
        except:
            sys.exit('Please make sure the output directory does not contain /voblist or /concats !!')
    return OutputPath # Returns validated output path


def TestISO(IsoPath):
    IsoPath = os.path.expanduser(IsoPath)
    # Checks to make sure it's pointed to VIDEO_TS
    if os.path.split(IsoPath)[-1] != 'VIDEO_TS':
        sys.exit('Not valid path to ISO files')
    elif not os.path.exists(IsoPath):
        sys.exit('VIDEO_TS folder does not exist.')
    return IsoPath # Returns validated source path


def VOBDict(VTSPath):
    vtsdict = defaultdict(list)
    for i in range(1,100):
        vtsindex = str(i).zfill(2)
        vtsbase = os.path.join(VTSPath, 'VTS_{0}'.format(vtsindex))
        for res in glob.glob('{0}*.VOB'.format(vtsbase)):
            vtsdict[vtsbase].append(res)
    return vtsdict


def CreateVOBLists(VTSDictionary, OutputPath):
    for f in VTSDictionary.iterkeys():
        textlist = os.path.join(OutputPath, 'voblists', '{0}_list.txt'.format(os.path.basename(f)))
        VTSDictionary[f].sort()
        with open(textlist, 'wb') as textlistfile:
            for vobfile in VTSDictionary[f]:
                textlistfile.write("file '{0}'\n".format(vobfile))
    return glob.glob(os.path.join(OutputPath, 'voblists', '*.txt'))


def ffmpegConcat(VOBLists, OutputPath):
    for vl in VOBLists:
        vlbasename = os.path.basename(vl.split('_list.txt')[0])
        vlbasename = '{0}_all.VOB'.format(vlbasename)
        vlbasename = os.path.join(OutputPath, 'concats', vlbasename)
        subprocess.check_output(['ffmpeg', '-f', 'concat', '-i', vl, '-c', 'copy', vlbasename])


def ffprobe(InputVOB):
    res = subprocess.check_output(['ffprobe', '-show_streams', '-i', InputVOB])
    for line in res.split('\n'):
        if line.startswith('height'):
            vobHeight = line.split('=', 1)[1].strip()
        if line.startswith('display_aspect_ratio'):
            vobDAR = line.split('=', 1)[1].strip()
    return vobHeight, vobDAR

def createFinal(OutputPath, InputFile, InputHeight, InputDAR):
    FinalVOB = os.path.basename(InputFile).split('_all.VOB')[0]
    FinalVOB = os.path.join(OutputPath, 'final_{0}'.format(TIMEDATE), '{0}_final.dv'.format(FinalVOB))
    if InputHeight == '480':
        FinalFormat = 'ntsc-dv'
    elif InputHeight == '576':
        FinalFormat = 'pal-dv'
    else:
        FinalFormat = 'ntsc-dv'
    try:
        subprocess.check_output(['ffmpeg', '-i', InputFile, '-target', FinalFormat, '-aspect', InputDAR, FinalVOB])
    except subprocess.CalledProcessError as e:
        print e.output
        sys.exit(1)


if __name__ == '__main__':
  main()
