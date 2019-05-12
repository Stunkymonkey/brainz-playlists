#!/usr/bin/env python
import os
import io
from pathlib import Path
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp3 import MP3
import argparse

music = dict()


def read_input_file(input_filename):
    with io.open(input_filename, 'r') as f:
        text = f.read()
        text = text.split("\n")
        lines = list(filter(None, text))
        return lines


def iterate_files(rootdir):
    for root, subdirs, files in os.walk(rootdir):
        for file in files:
            file_path = os.path.join(root, file)
            read_data(file_path)


def read_data(file):
    try:
        tags = ID3(file)
    except ID3NoHeaderError:
        return
    audio = MP3(file)
    if "TIT2" in tags:
        artist = tags["TIT2"].text[0]
    if "TPE1" in tags:
        title = tags["TPE1"].text[0]
    if "TXXX:MusicBrainz Release Track Id" in tags:
        brainz_id = tags["TXXX:MusicBrainz Release Track Id"].text[0]
    else:
        return
    length = audio.info.length
    if brainz_id in music:
        music[brainz_id] = file, artist, title, length


def generate_m3u8(output_filename):
    with io.open(output_filename, "w", encoding="utf8") as f:
        f.write("#EXTM3U\n")
        for value in music.values():
            if len(value) != 4:
                continue
            f.write("\n#EXTINF:" + str(value[3]) + "," + value[1] + " - " + value[2] + "\n")
            f.write(value[0] + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file with music-brainz-ids")
    parser.add_argument("output", help="output file")
    parser.add_argument("music", help="path of your music", nargs='?', default=str(Path.home()) + "/Music/")
    args = parser.parse_args()

    path = args.music
    input_filename = args.input
    output_filename = args.output

    lines = read_input_file(input_filename)
    for line in lines:
        music[line] = list()

    iterate_files(path)
    generate_m3u8(output_filename)


if __name__ == '__main__':
    main()
