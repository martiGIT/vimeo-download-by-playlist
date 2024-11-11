import subprocess
import requests
import shutil
import os
import re
import json
import argparse

"""
Vimeo Video Downloader
Original idea and most of the implementation by sk8ordi3 (https://github.com/sk8ordi3)
Source: https://forum.videohelp.com/threads/414958-How-to-download-vimeo-video-from-a-new-stream-url/page2#post2741697

Modified to use system tools and work on Linux.
"""

def parse_args():
    parser = argparse.ArgumentParser(
        description='Download videos from Vimeo using v2 playlist.json links',
        epilog='Example: python3 download.py'
    )
    parser.add_argument('-a', '--auto', choices=['yes', 'no'], default='yes',
                      help='Auto select best quality (default: yes)')
    return parser.parse_args()

args = parse_args()

# 'yes' for auto best selection or 'no' for manual selection
auto_best = args.auto

dirs_to_cr = [
    'bin', 'Downloads/Finished/Vimeo', 'Downloads/Temp'
]

for directory_path in dirs_to_cr:
    os.makedirs(directory_path, exist_ok=True)

temp_dir = 'Downloads/Temp'
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

# Use system tools
yt_dl = 'yt-dlp'
ffm = 'ffmpeg'

# Check if required tools are available
try:
    subprocess.run([yt_dl, '--version'], capture_output=True, check=True)
except (subprocess.CalledProcessError, FileNotFoundError):
    print("yt-dlp is not installed. Install using: pip install yt-dlp")
    ex_it = input('Press Enter to exit....')
    exit()

try:
    subprocess.run([ffm, '-version'], capture_output=True, check=True)
except (subprocess.CalledProcessError, FileNotFoundError):
    print("ffmpeg is not installed. Install using your system's package manager")
    ex_it = input('Press Enter to exit....')
    exit()

print('''
Vimeo Video Downloader
Original idea and implementation by sk8ordi3 (https://github.com/sk8ordi3)
Source: https://forum.videohelp.com/threads/414958-How-to-download-vimeo-video-from-a-new-stream-url/page2#post2741697

Please provide v2 playlist.json link
''')

link = input('Link: ')

try:
    bef_v2 = re.findall(r'(https:.*exp.*hmac.*)/v2/playlist', link)[0].strip()
except IndexError:
    print(' [ERROR] this is not a v2 playlist.json link!')
    ex_it = input('\nPress Enter to close..')
    exit()    

video_title = input('\nVideo title here: ')

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

resp = requests.get(link, headers=headers).json()

# Debug - display response structure
print("\nDEBUG: Response structure:")
print(json.dumps(resp, indent=2))

# Check available keys in response
print("\nDEBUG: Available keys in response:")
print(resp.keys())

# Adapt to response structure
video_streams = resp.get('video', [])  # or different key containing video streams
audio_streams = resp.get('audio', [])  # or different key containing audio streams

if not video_streams:
    print(" [ERROR] No video streams found in response!")
    exit()

video_data = [
    {
        'id': re.match(r'(.*?)-', video['id']).group(1),
        'width': video.get('width', 0),
        'height': video.get('height', 0),
        'video_res': f"{video.get('width', 0)}x{video.get('height', 0)}",
        'video_link': f"{bef_v2}/parcel/video/{re.match(r'(.*?)-', video['id']).group(1)}.mp4"
    }
    for video in video_streams
]

audio_data = [
    {
        'id': re.match(r'(.*?)-', audio['id']).group(1),
        'codecs': audio.get('codecs', 'unknown'),
        'bitrate': audio.get('bitrate', 0),
        'audio_details': f"{audio.get('codecs', 'unknown')}, {audio.get('bitrate', 0)}",
        'audio_link': f"{bef_v2}/parcel/audio/{re.match(r'(.*?)-', audio['id']).group(1)}.mp4"
    }
    for audio in audio_streams
]

# Sort video and audio streams by quality (highest first)
video_data.sort(key=lambda x: (x['width'], x['height']), reverse=True)
audio_data.sort(key=lambda x: x['bitrate'], reverse=True)

sel_vid_name = None
sel_aud_name = None

options = []

if auto_best == 'no':
    print("\nAvailable options:")

# Prepare video options
for idx, video in enumerate(video_data, start=1):
    video_id = video['id']
    video_res = video['video_res']
    options.append((idx, f"video | {video_res} | {video_id}", video['video_link']))
    
    if auto_best == 'no':
        print(f"{idx} - video | {video_res}")

# Prepare audio options
for idx, audio in enumerate(audio_data, start=len(video_data) + 1):
    audio_id = audio['id']
    audio_details = audio['audio_details']
    options.append((idx, f"audio | {audio_details} | {audio_id}", audio['audio_link']))
    
    if auto_best == 'no':
        print(f"{idx} - audio | {audio_details}")

# Auto best quality selection
if auto_best == 'yes':
    sel_vid_name = video_data[0]['video_res']
    selected_video_link = video_data[0]['video_link']
    sel_aud_name = audio_data[0]['audio_details']
    selected_audio_link = audio_data[0]['audio_link']
    print(f"\nbest video: {sel_vid_name}")
    print(f"best audio: {sel_aud_name}\n")
    
    subprocess.run([yt_dl, '-N', '16', '--no-warning', '--no-check-certificate', '-o', f'{temp_dir}/{sel_vid_name}.mp4', selected_video_link])
    print()
    subprocess.run([yt_dl, '-N', '16', '--no-warning', '--no-check-certificate', '-o', f'{temp_dir}/{sel_aud_name}.aac', selected_audio_link])

# Manual quality selection
if auto_best == 'no':
    selection = input("Write numbers here (one video, one audio e.g; 1 4): ").split()
    selection = [int(num) for num in selection]
    
    selection_str = ', '.join(map(str, selection))
    
    print(f'\nSelected: {selection_str}')
    
    for num in selection:
        for option in options:
            if option[0] == num:
                print(f"\nProcessing: {num}")
                if "video" in option[1]:
                    sel_vid_name = option[1].split('|')[1].strip()
                    selected_video_link = option[2]
                    print(f"{sel_vid_name}\n")
                    
                    subprocess.run([yt_dl, '-N', '16', '--no-warning', '--no-check-certificate', '-o', f'{temp_dir}/{sel_vid_name}.mp4', selected_video_link])
                elif "audio" in option[1]:
                    sel_aud_name = option[1].split('|')[1].strip()
                    selected_audio_link = option[2]
                    print(f"{sel_aud_name}\n")
                    
                    subprocess.run([yt_dl, '-N', '16', '--no-warning', '--no-check-certificate', '-o', f'{temp_dir}/{sel_aud_name}.aac', selected_audio_link])

# Merge video and audio if both were selected
if sel_vid_name and sel_aud_name:
    output_x = f'Downloads/Finished/Vimeo/{sel_vid_name}_{video_title}.mp4'
    
    print('\n [INFO] ffmpeg process started...\n')
    subprocess.run([ffm, '-v', 'quiet', '-stats', '-y', '-i', f'{temp_dir}/{sel_vid_name}.mp4', '-i', f'{temp_dir}/{sel_aud_name}.aac', '-c', 'copy', output_x])
else:
    print("\n [ERROR] Need video and audio picked..")

print(f'\n [INFO] file moved here:\n {output_x}')

print('\n [INFO] Deleting temporary files..')

temp_dir = 'Downloads/Temp'
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

print(' [INFO] All done.')
ex_it = input('\nPress Enter to close..')
exit()