import requests, sys, shutil, math, os, subprocess

from datetime import datetime, timezone
# Script currently creates a video using all videos in folder... modify to be able to specify # of hours in timelapse

# Inputs ----
# Location to store images
path_root = "your/directory/here"
# specify view = 'conus' or 'full disk'
view = "full disk"
# number of hours to include in timelapse video
timelapse_hours = 24
# video framerate
framerate = 24
# Video file name:
output_wallpaper = "output1.mp4"
# Looped and reversed video file name:
output_looped = "output2.mp4"
# -----------

# parameters
minutes_between_images_conus = 5
minutes_between_images_fd = 10
if view == 'conus':
    minutes_between_images = minutes_between_images_conus
else:
    minutes_between_images = minutes_between_images_fd
images_per_hour = int(60/minutes_between_images)
num_images = int(images_per_hour*timelapse_hours)

class timestamp:
    def __init__(self, year, day, hour, minute, by):
        self.year = year
        self.day = day
        self.hour = hour
        self.minute = minute
        self.by = by
        self.clean
    def now_fd():
        now = datetime.now(timezone.utc)
        year = str(now.timetuple().tm_year)
        day = str(now.timetuple().tm_yday)
        hour = str(now.timetuple().tm_hour)
        minute = str(math.floor(now.timetuple().tm_min / 10) * 10)
        ts = timestamp(year, day, hour, minute, by=10)
        ts.next().next()
        return ts
    def now_conus():
        now = datetime.now(timezone.utc)
        year = str(now.timetuple().tm_year)
        day = str(now.timetuple().tm_yday)
        hour = str(now.timetuple().tm_hour)
        minute = str(math.floor(now.timetuple().tm_min / 5) * 5 + 1)
        ts = timestamp(year, day, hour, minute, by=5)
        ts.next()
        return ts
    def clean_minute(self):
        if len(self.minute)<2:
            self.minute = '0'+self.minute
    def clean_hour(self):
        if len(self.hour)<2:
            self.hour = '0'+self.hour
    def clean_day(self):
        if len(self.day)<2:
            self.day = '0'+self.day
    def clean(self):
        self.clean_minute()
        self.clean_hour()
        self.clean_day()
    def get(self):
        self.clean()
        return(self.year + self.day + self.hour + self.minute)
    def next(self):
        if int(self.minute) < int(self.by):
            self.minute=str(60+int(self.minute)-int(self.by))
            if self.hour=="00":
                self.hour="23"
                self.day=str(int(self.day)-1)
            else:
                self.hour=str(int(self.hour)-1)
        else:
            self.minute=str(int(self.minute)-self.by)
        self.clean()
        return self
    def prev(self):
        if int(self.minute) + int(self.by) >= 60:
            self.minute=str(int(self.minute)+int(self.by)-60)
            if self.hour=="23":
                self.hour="00"
                self.day=str(int(self.day)+1)
            else:
                self.hour=str(int(self.hour)+1)
        else:
            self.minute=str(int(self.minute)+self.by)
        self.clean()
        return self

if view == 'conus':
    ts = timestamp.now_conus()
else:
    ts = timestamp.now_fd()
ts.get()

for i in range(num_images):
    if view == 'conus':
        url = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/CONUS/GEOCOLOR/"+ts.get()+"_GOES16-ABI-CONUS-GEOCOLOR-10000x6000.jpg"
    else:
        url = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/FD/GEOCOLOR/"+ts.get()+"_GOES16-ABI-FD-GEOCOLOR-10848x10848.jpg"

    path_output = path_root+ts.get()+".jpg"
    
    if not os.path.isfile(path_output):
        data = requests.get(url).content
        if sys.getsizeof(data) < 6000000:
            shutil.copyfile(path_root+ts.prev().get()+".jpg", path_output)
            ts.next()
        else:
            with open(path_output,'wb') as f:
                f.write(data)
    ts.next()
    print(ts.get())

import subprocess
 
# Edit this to only use # of hours specified above in the backfill...
def count_jpeg_files(folder_path):
    jpeg_count = 0
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpeg'):
            jpeg_count += 1
    return jpeg_count

num_jpeg = count_jpeg_files(path_root)

# currently set to 1440p resolution, check scale option in rc1 below if need to adjust:
rc1 = subprocess.run("ffmpeg -y -framerate "+str(framerate)+" -pattern_type glob -i '"+path_root+"*.jpg' -vf 'scale=-1:1440,pad=2560:1440:(ow-iw)/2:(oh-ih)/2' '"+path_root+output_wallpaper+"'", shell=True)
rc2 = subprocess.run("ffmpeg -y -i '"+path_root+"output1.mp4' -filter_complex '[0]reverse[r];[0][r]concat,loop=1:" +str(num_jpeg/framerate*2)+",setpts=N/"+str(framerate)+"/TB' '"+path_root+output_looped+"'", shell=True)
