# Vimeo Playlist Downloader

Download Vimeo private videos using v2 playlist.json links. This tool allows you to download video and audio streams separately and merge them into a single file, with options for both automatic best quality selection and manual quality choice.

Original idea and most of the implementation by [sk8ordi3](https://github.com/sk8ordi3).  
Source: [VideoHelp Forum Thread](https://forum.videohelp.com/threads/414958-How-to-download-vimeo-video-from-a-new-stream-url/page2#post2741697)

## Description
This version is modified to:
- Use system tools instead of bundled binaries
- Work natively on Linux systems
- Support both automatic and manual quality selection
- Handle modern Vimeo playlist.json structures

## Requirements
- Python 3.6+
- yt-dlp: `pip install yt-dlp`
- ffmpeg: install via your system's package manager
- requests: `pip install requests`

## Installation
1. Clone this repository:
```bash
git clone https://github.com/yourusername/vimeo-dl-by-playlist.git
cd vimeo-dl-by-playlist
```

2. Install required Python packages:
```bash
pip install requests yt-dlp
```

3. Make sure ffmpeg is installed:
```bash
# On Ubuntu/Debian:
sudo apt install ffmpeg

# On Fedora:
sudo dnf install ffmpeg

# On Arch Linux:
sudo pacman -S ffmpeg
```

## Usage
Basic usage:
```bash
python3 vimeo-dl-by-playlist.py
```

With manual quality selection:
```bash
python3 vimeo-dl-by-playlist.py --auto no
```

Show help:
```bash
python3 vimeo-dl-by-playlist.py -h
```

## How to get the playlist.json link
1. Open the Vimeo video page
2. Open Developer Tools (F12 in most browsers)
3. Go to the Network tab
4. Play the video
5. Look for a request URL containing "v2/playlist.json"
6. Copy the full URL - it should contain "exp" and "hmac" parameters

## Features
- Automatic best quality selection
- Manual quality selection option
- Separate video and audio stream download
- Automatic merging using ffmpeg
- Temporary file cleanup
- Progress display during download
- Error handling and user feedback

## Output Structure
Downloaded files are organized as follows:
```
Downloads/
├── Finished/
│   └── Vimeo/
│       └── [resolution]_[title].mp4
└── Temp/
    ├── [temporary video files]
    └── [temporary audio files]
```

## Known Limitations
- Works only with v2 playlist.json links
- Links are time-sensitive and expire
- Requires manual extraction of playlist URL
- Some videos might be protected or region-locked

## Contributing
Feel free to open issues and pull requests!

## License
[MIT License](LICENSE)