#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DVD Transcoder
# Version History
#   0.1.0 - 20180314
#       Got it mostly working. current known issues:
#           No Aspect Ratio Testing
#
#
# import modules used here -- sys is a very standard one
import os, sys
import datetime
import csv  # used for creating the csv
import subprocess  # used for running ffmpeg, qcli, and rsync
import shlex  # used for properly splitting the ffmpeg/rsync strings
import argparse  # used for parsing input arguments
import shutil
import tempfile

from dvd2ls import iso
import time


def main():


    media_info_list = []

    ####init the stuff from the cli########
    parser = argparse.ArgumentParser(description="dvd_transcoder version 0.1.0: Creates a concatenatd video file from an DVD-Video ISO")
    parser.add_argument('-i','--input',dest='i', help="the path to the input directory or files")
    parser.add_argument('-f','--format',dest='f', help="The output format (defaults to v210. Pick from v210, ProRes, H.264, FFv1)")
    parser.add_argument('-o','--output',dest='o', help="the output file path (optional, defaults to the same as the input)")
    parser.add_argument('-v','--verbose',dest='v',action='store_true',default=False,help='run in verbose mode (including ffmpeg info)')
    #parser.add_argument('-c','--csvname',dest='c', help="the name of the csv file (optional)")
    args = parser.parse_args()

    # handling the input args. This is kind of a mess in this version
    if args.i is None:
        print(bcolors.FAIL + "Please enter an input file!" + bcolors.ENDC)
        quit()
    if args.f is None:
        output_format = "H.264"
        transcode_string = " -c:v libx264 -pix_fmt yuv420p -movflags faststart -b:v 3500000 -b:a 160000 -ar 48000 -s 640x480 -vf yadif "
        output_ext = ".mp4"
    elif "v210" in args.f:
        output_format = "v210"
        transcode_string = " -movflags write_colr+faststart -color_primaries smpte170m -color_trc bt709 -colorspace smpte170m -color_range mpeg -vf 'setfield=bff,setdar=4/3' -c:v v210 -c:a pcm_s24le "
        output_ext = ".mov"
    elif "ProRes" in args.f:
        output_format = "ProRes"
        transcode_string = " -c:v prores_ks -profile:v 3 -c:a pcm_s24le "
        output_ext = ".mov"
    elif "H.264" in args.f:
        output_format = "H.264"
        transcode_string = " -c:v libx264 -pix_fmt yuv420p -movflags faststart -b:v 3500000 -b:a 160000 -ar 48000 -s 640x480 -vf yadif "
        output_ext = ".mp4"
    elif "FFv1" in args.f:
        output_format = "FFv1"
        transcode_string = " -map 0 -dn -c:v ffv1 -level 3 -coder 1 -context 1 -g 1 -slicecrc 1 -slices 24 -field_order bt -color_primaries smpte170m -color_trc bt709 -colorspace smpte170m -c:a copy "
        output_ext = ".mkv"
    else:
        output_format = "v210"
        transcode_string = " -movflags write_colr+faststart -color_primaries smpte170m -color_trc bt709 -colorspace smpte170m -color_range mpeg -vf 'setfield=bff,setdar=4/3' -c:v v210 -c:a pcm_s24le "
        output_ext = ".mov"
    if args.o is None:
        output_path = os.path.dirname(args.i) + "/"

    if args.v:
        ffmpeg_command = "/usr/local/bin/ffmpeg"
    else:
        ffmpeg_command = "/usr/local/bin/ffmpeg -hide_banner -loglevel panic"
        print("Running in Verbose Mode")

    print("Removing Temporary Files")

    # This parts mounts the iso
    # print("Mounting ISO...")
    extractor = iso.Extractor(args.i)
    temp_dir = tempfile.mkdtemp()
    mount_point = os.path.dirname(os.path.join(temp_dir, "extractor"))
    with extractor as e:
        for file_path, compressed_file in e:
            print("Extracting {}".format(compressed_file.name.decode()))
            # dst = os.path.dirname(os.path.join(temp_dir, "extractor"))
            e.extract(compressed_file, dest=mount_point)

    # this part processes the vobs
    # move each vob over as a seperate file, adding each vob to a list to be
    # concatenated

    print("Moving VOBs to Local directory...")
    move_VOBS_to_local(args.i, mount_point, ffmpeg_command)

    # concatenate vobs into a sungle file, format of the user's selection
    concatenate_VOBS(args.i, transcode_string, output_ext, ffmpeg_command)

    # CLEANUP
    print("Removing Temporary Files...")
    # Delete all fo the leftover files
    os.remove(args.i + ".mylist.txt")
    for the_file in os.listdir(args.i + ".VOBS"):
        file_path = os.path.join(args.i + ".VOBS", the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
    os.rmdir(args.i + ".VOBS")
    print("Finished Removing Temporary Files!")


    return


def move_VOBS_to_local(temp_destination, vob_source, ffmpeg_command):
    # find all of the vobs we want to concatenate
    input_vobList = find_all_vobs(vob_source)

    # this portion performs the copy of the VOBs to the SAN. They are
    # concatenated after the copy so the streams are in the right order

    vob_temp_dir = temp_destination + ".VOBS/"

    try:
        os.mkdir(vob_temp_dir)
    except OSError:
        pass
    stream_copy_vobs_to_temp_dir(ffmpeg_command, input_vobList, vob_temp_dir)
    # writing list of vobs to concat
    vob_list_file = temp_destination + ".mylist.txt"

    write_voblist_file(vob_list_file, input_vobList, vob_temp_dir)

    return True


def write_voblist_file(filename, input_vobList, vob_temp_dir):
    with open(filename, "w") as f:
        for v in input_vobList:
            v_name = v.split("/")[-1]
            out_vob_path = vob_temp_dir + v_name
            f.write("file '" + out_vob_path + "'")
            f.write("\n")


def stream_copy_vobs_to_temp_dir(ffmpeg_command, input_vobList, vob_temp_dir):
    for v in input_vobList:
        # print(v)
        v_name = v.split("/")[-1]
        # print(v_name)
        out_vob_path = vob_temp_dir + v_name

        command = ffmpeg_command.split(" ")
        command += [
            "-i", v,
            "-map", "0:v:0", "-map", "0:a:0?",
            "-f", "vob", "-b:v", "9M", "-b:a", "192k", "-y",
            out_vob_path
        ]
        # "]
        run_command(command)


def find_all_vobs(search_path):

    input_vobList = []
    for dirName, subdirList, fileList in os.walk(search_path):
        for fname in fileList:
            if fname.split("_")[0] == "VTS" and fname.split(".")[-1] == "VOB":
                vobNum = fname.split("_")[-1]
                vobNum = vobNum.split(".")[0]
                vobNum = int(vobNum)
                if vobNum > 0:
                    input_vobList.append(dirName + "/" + fname)
    if len(input_vobList) == 0:
        raise FileNotFoundError("No Vobs located in {}".format(search_path))
    else:
        input_vobList.sort()
    return input_vobList


def concatenate_VOBS(first_file_path, transcode_string, output_ext, ffmpeg_command):
    command = [
        "ffmpeg",
        "-vsync", "0", "-f", "concat", "-safe", "0",
        "-i"
    ]
    catList = first_file_path + ".mylist.txt"
    command.append(catList)
    command += transcode_string.split()

    extension = os.path.splitext(first_file_path)[1]
    output_path = first_file_path.replace(extension, output_ext)
    command.append("-y")
    command.append(output_path)
    # print(" ".join(command))
    # print(command)
    run_command(command)
    # print("concat done")

    # ffmpeg_vob_concat_string = ffmpeg_command + " -vsync 0 -f concat -safe 0 -i '" + catList + "' " + transcode_string + " '" + output_path + "'"

    # print(ffmpeg_vob_concat_string)
    # run_command(ffmpeg_vob_concat_string)


def run_command(command):
    # output = subprocess.run(command, shell=True)
    # print(" ".join(command))
    output = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output.communicate()
    # print(output.stdout)
    # print(output.stderr)
    return output.stdout,output.stderr

# Used to make colored text
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
