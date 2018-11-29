import pytest

from dvd2dv25 import dvd_transcoder
import subprocess
import os


class GetCommand(ValueError):

    def __init__(self, cli_args, *args):
        super(ValueError, self).__init__(*args)
        self.cli_args = cli_args


@pytest.fixture
def no_running(monkeypatch):
    def return_command_instead(args, **kwargs):
        raise GetCommand(args)

    def print_mkdir(*args, **kwargs):
        pass

    monkeypatch.setattr(dvd_transcoder, "run_command", return_command_instead)
    monkeypatch.setattr(os, "mkdir", print_mkdir)
    return


def test_mount_Image(no_running):
    try:
        dvd_transcoder.mount_Image("dummy.iso")
    except GetCommand as command:
        expected_args = [
            "hdiutil",
            "attach",
            "dummy.iso",
            "-mountpoint",
            "/private/tmp/ISO_Volume_0"
        ]
        assert expected_args == command.cli_args


def test_unmount_Image(no_running):
    try:
        dvd_transcoder.unmount_Image("/tmp/ISO_Volume_0")
    except GetCommand as command:
        expected_args = [
            "hdiutil",
            "detach",
            "/tmp/ISO_Volume_0"
        ]
        assert expected_args == command.cli_args


def test_concatenate_VOBS(no_running):
    try:
        dvd_transcoder.concatenate_VOBS(
            first_file_path="/tmp/dummy.iso",
            transcode_string="-c:v prores_ks -profile:v 3 -c:a pcm_s24le",
            output_ext=".mov",
            ffmpeg_command="ffmpeg"

        )
    except GetCommand as command:
        expected_args = [
            "ffmpeg",
            "-vsync", "0",
            "-f", "concat", "-safe", "0",
            "-i", '/tmp/dummy.iso.mylist.txt',
            "-c:v", "prores_ks",
            "-profile:v", "3",
            "-c:a", "pcm_s24le",
            '/tmp/dummy.mov'
        ]
        assert expected_args == command.cli_args
