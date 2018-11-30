AMIA Hack Day 2018
==================

November 28, 2018

*NOTE: This document exists to define basic terminology and workflow that could serve as helpful entry points for community members who might have trouble understanding our documentation on this project*

Project to be revived:
----------------------

DVD generation
HOW DO WE JUST RIP DVDs to MP4 (for quick transcodes)
Generate scripts COMBINED with workflow documentation for a basic how-to
Proposed by Kathryn Gronsbell and Ben Turkus

PROJECT: DVD transcoder

Github repository: https://github.com/amiaopensource/DVD2LS

Ripping the DVD // possible to do with CLI tools for free on any computer
Issue: script works but it’s not super accessible
Goal: create an app that can transcode/perform the function of the script with more ease
Grand scheme: the UI prompts user to choose which device they’re using and allows them to define input formats and output directory

About the script
----------------

Two parts of the code:

Part where we make the file from the ISO exists
Part where we actually make the ISO from a DVD

Workflow
________

Step one: Rip the dvd and create an ISO for your “preservation file”
Step two (for access/production needs): Need to get information from ISO into a file -- tricky because DVD structures with MPEG-2 are difficult

How to run the sample (in terminal): drop in DVD transcode python script + ISO

Updates to the code have fixed mountpoint issues. The ISO no longer needs to be mounted in order to have the data extracted.

Goal
----

Rip the DVD
Create the ISO
Transcode the .VOBs inside the ISO to an access format (like DV)
Output into a directory

Terminology
-----------

ISO: an image/container -- “like a zip file with no compression and contains a location for every bit.” You would rip a DVD to an ISO for a preservation master/bit copy of a DVD for digital storage rather than optical storage

Concatenate: joining or merging media files: https://trac.ffmpeg.org/wiki/Concatenate

Mounting: process by which you make one filesystem (like a DVD on a drive) available to a larger system (like an OS): http://tldp.org/LDP/Linux-Filesystem-Hierarchy/html/mnt.html

.vob: Video Object, container format for DVDs that can contain video, audio, subtitles, dvd menus, and navigation contents: https://en.wikipedia.org/wiki/VOB

.dv: Digital Video format, easier to use than .vob: https://www.openwith.org/file-extensions/dv/465

Useful/necessary software/tools

JetBrains Toolbox: Launchpad for JetBrains tools including PyCharm (see below)

PyCharm: a Python-specific integrated development environment, works with git/github. Pro version is available to students/people with.edu emails for free: https://www.jetbrains.com/pycharm/

Tox -- Python tool for running tests, don’t need to install, it’s a dev tool

Travis CI

ddrescue: basic disc imaging tool

Working in PyCharm/Git
----------------------

Two versions where the “remote” is stored:
Local copy (created from original on amia open source)
Upstream: on AMIA open source



Hot tips
________

Command shift G -- go to folder

Questions
_________

Which operating systems do we want to support?

Basic tools we found useful/wish we had

Whiteboard/dry erase markers!
DVD drive
DVDs