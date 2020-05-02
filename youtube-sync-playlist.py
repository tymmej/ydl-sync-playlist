#!/usr/bin/env python3

import glob
import os
import re
import shutil
import youtube_dl

COOKIES = "/home/tymmej/cookies.txt"
DIR = "/storage/Videos/youtube"
INFO_FILE = "%s/info.txt" % DIR
OUTPUT_FORMAT = "%(upload_date)s/%(uploader)s - %(title)s.%(ext)s"
OUTPUT_FILE = "%s/%s" % (DIR, OUTPUT_FORMAT)
VIDEO_FORMAT = 'bestvideo[height<=1080,ext=mp4]+bestaudio'
PLAYLIST = 'https://www.youtube.com/playlist?list=WL'

def youtube_get_playlist(playlist):
    ydl = youtube_dl.YoutubeDL({'dump_single_json': True,
                                'extract_flat' : True,
                                'cookiefile' : COOKIES})

    videos = None

    with ydl:
        videos = ydl.extract_info(playlist, False)

    return videos['entries']


def youtube_get_video(video_id):
    url = 'https://www.youtube.com/watch?v=%s' % video_id
    print("Downloading %s" % url)

    ydl = youtube_dl.YoutubeDL({'outtmpl': OUTPUT_FILE,
                                'format' : VIDEO_FORMAT,
                                'cookiefile' : COOKIES})

    info = ydl.extract_info(url, download=False)
    filename = ydl.prepare_filename(info)
    print("%s is %s" % (video['id'], filename))

    ydl.download([url])

    filename = os.path.splitext(filename)[0]

    files = glob.glob(filename + "*")
    if len(files) != 1:
        raise Exception("Weird")

    filename = files[0]

    return filename

def load_info(info_file):
    if not os.path.isfile(info_file):
        return {}

    with open(info_file, "r") as f:
        data = f.read()

    videos = data.splitlines()

    videos_dict = {}
    for video in videos:
        video_id, video_filename = video.split(':')
        videos_dict[video_id] = video_filename

    return videos_dict

def remove_deleted_videos(info_file, directory):
    for root, _, files in os.walk(directory):
        for name in files:
            filename = os.path.join(root, name)
            if os.path.splitext(filename)[0] not in info_file.values() or name == COOKIE:
                print("Deleting %s" % filename)
                os.remove(filename)
            if not os.listdir(root):
                os.rmdir(root)

if __name__ == "__main__":
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    info_file = load_info(INFO_FILE)

    videos = youtube_get_playlist(PLAYLIST)

    new_info_file = {}

    f = open(INFO_FILE, "w")

    for video in videos:
        if video['id'] in info_file.keys():
            print("File %s already exists" % video['id'])
            filename = info_file[video['id']]
        else:
            try:
                filename = youtube_get_video(video['id'])
                new_filename = re.sub('[^A-Za-z0-9#/ \-\.]+', '', filename)
                shutil.move(filename, new_filename)
                filename = new_filename
                filename = os.path.splitext(filename)[0]
            except youtube_dl.utils.DownloadError:
                print("Private video %s" % video['id'])
                continue

        new_info_file[video['id']] = filename
        f.write("%s:%s\n" % (video['id'], filename))
        f.flush()

    f.close()

    remove_deleted_videos(new_info_file, DIR)
