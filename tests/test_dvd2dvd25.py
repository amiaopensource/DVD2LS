import pytest

from dvd2ls import dvd_transcoder
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
            "-y",
            '/tmp/dummy.mov'
        ]
        assert expected_args == command.cli_args
