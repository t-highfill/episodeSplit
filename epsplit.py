#!/usr/bin/python3

import subprocess
import json
import argparse
import sys

DEFAULT_FORMAT = "{episode_num:02d}{title}.{ext}"
DEFAULT_STARTNUM = 1
DEFAULT_LENGTH = 1
DEFAULT_EXTRAS = "warn"
DEFAULT_SKIP = 0
DEFAULT_TITLE_PROMPT = False


def getChapters(fname):
    proc = subprocess.run(["ffprobe", "-i", fname, "-print_format", "json",
                           "-show_chapters", "-loglevel", "error"],
                           check=True, capture_output=True)
    dat = json.loads(proc.stdout)
    return dat["chapters"]


def epsplit(fnames, format=DEFAULT_FORMAT, startnum=DEFAULT_STARTNUM, length=DEFAULT_LENGTH, extras=DEFAULT_EXTRAS, skip=DEFAULT_SKIP, titlePrompt=DEFAULT_TITLE_PROMPT, episodes=None):
    episode_num = startnum
    ep_count = 0
    if ep_count == episodes:
        return
    for fname in fnames:
        file_ext = fname.split('.')[-1]
        chapters = getChapters(fname)
        ch_cnt = len(chapters)
        ch_idx = skip
        extra_cnt = (ch_cnt - ch_idx) % length
        if extra_cnt > 0:
            message = "Found {} unused chapters at the end\n".format(extra_cnt)
            if extras == "warn":
                print("WARNING: " + message, file=sys.stderr, flush=True)
            elif extras == "error":
                print("ERROR: " + message, file=sys.stderr, flush=True)
                sys.exit(extra_cnt)
        while ch_idx + length - 1 < ch_cnt:
            start = chapters[ch_idx]["start_time"]
            end = chapters[ch_idx + length - 1]["end_time"]
            title = ""
            if titlePrompt:
                title = input("Title for episode {}: ".format(episode_num))
            outfile = format.format(episode_num=episode_num,
                                    ext=file_ext, title=title)
            subprocess.run(["ffmpeg", "-ss", start, "-to", end, "-i",
                            fname, "-map", "0", "-codec", "copy",
                            "-max_interleave_delta", "0", outfile],
                            check=True)
            ch_idx += length
            episode_num += 1
            ep_count += 1
            if ep_count == episodes:
                return

def main():
    parser = argparse.ArgumentParser(prog='epsplit',
        description="Split a video by episode with chapters")
    parser.add_argument("inFiles", nargs='+', help="The video files to split, in order")
    parser.add_argument("--format", default=DEFAULT_FORMAT,
                        help="Format for the output filenames")
    parser.add_argument("--startnum", type=int,
                        default=DEFAULT_STARTNUM,
                        help="Episode number to start with")
    parser.add_argument("--length", type=int, default=DEFAULT_LENGTH,
                        help="Length of an episode in chapters")
    parser.add_argument("--episodes", type=int, default=None,
                        help="Max number of episodes to pull")
    parser.add_argument("--extras", default=DEFAULT_EXTRAS, choices=[
                        "warn", "drop", "error"],
                        help="Specifies how extra chapters should be handled")
    parser.add_argument("--skip", type=int, default=DEFAULT_SKIP,
                        help="Number of chapters to skip at the beginning")
    parser.add_argument("--title-prompt", action="store_true",
                        help="Prompt for each episode title")
    

    args = parser.parse_args()
    # print(args)
    epsplit(args.inFiles, format=args.format, startnum=args.startnum,
            length=args.length, extras=args.extras, skip=args.skip,
            titlePrompt=args.title_prompt, episodes=args.episodes)


if __name__ == '__main__':
    main()
