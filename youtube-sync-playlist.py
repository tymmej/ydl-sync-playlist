#!/usr/bin/env python3

import glob
import os
import re
import shutil
import youtube_dl

COOKIES = "/home/tymmej/cookies.txt"
DIR = "/storage/Videos/youtube"
OUTPUT_FORMAT = "%(upload_date)s/%(uploader)s - %(title)s.%(ext)s"
OUTPUT_FILE = "%s/%s" % (DIR, OUTPUT_FORMAT)
VIDEO_FORMAT = 'bestvideo[height<=1080,ext=mp4]+bestaudio'
PLAYLIST = 'https://www.youtube.com/playlist?list=WL'
REPLACE='[^A-Za-z0-9#/ \-\.]+'

def youtube_get_playlist(playlist):
    ydl = youtube_dl.YoutubeDL({'dump_single_json': True,
                                'extract_flat' : True,
                                'cookiefile' : COOKIES})

    videos = None

    with ydl:
        videos = ydl.extract_info(playlist, False)

    return videos['entries']

def file_present(video_id):
    url = 'https://www.youtube.com/watch?v=%s' % video_id
    print("Downloading %s" % url)

    ydl = youtube_dl.YoutubeDL({'outtmpl': OUTPUT_FILE,
                                'format' : VIDEO_FORMAT,
                                'cookiefile' : COOKIES})

    info = ydl.extract_info(url, download=False)
    filename = ydl.prepare_filename(info)
    print("%s is %s" % (video['id'], filename))
    
    filename = os.path.splitext(filename)[0]

    new_filename = re.sub(REPLACE, '', filename)
    
    files = glob.glob(new_filename + "*")
    if len(files) == 1 and not files[0].endswith(".part"):
        print("File present")
        return (True, new_filename)
    else:
        return (False, filename)

def youtube_get_video(video_id):
    present, filename = file_present(video_id)
    if present:
        return filename

    url = 'https://www.youtube.com/watch?v=%s' % video_id
    print("Downloading %s" % url)

    ydl = youtube_dl.YoutubeDL({'outtmpl': OUTPUT_FILE,
                                'format' : VIDEO_FORMAT,
                                'cookiefile' : COOKIES})
    
    ydl.download([url])
    
    files = glob.glob(glob.escape(filename) + "*")
    if len(files) != 1:
        raise Exception("Weird")

    filename = files[0]
    
    new_filename = re.sub(REPLACE, '', filename)
    shutil.move(filename, new_filename)
    filename = new_filename
    filename = os.path.splitext(filename)[0]

    return filename

def remove_deleted_videos(info_file, directory):
    for root, _, files in os.walk(directory):
        for name in files:
            filename = os.path.join(root, name)
            if os.path.splitext(filename)[0] not in info_file.values():
                print("Deleting %s" % filename)
                os.remove(filename)
            if not os.listdir(root):
                os.rmdir(root)

if __name__ == "__main__":
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    new_info_file = {}

    videos = youtube_get_playlist(PLAYLIST)

    for video in videos:
        try:
            filename = youtube_get_video(video['id'])
        except youtube_dl.utils.DownloadError:
            print("Private video %s" % video['id'])
            continue

        new_info_file[video['id']] = filename
    
    remove_deleted_videos(new_info_file, DIR)

