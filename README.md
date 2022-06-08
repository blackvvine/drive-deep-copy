# GDrive Deep Copy

<a href="https://github.com/blackvvine/drive-deep-copy/stargazers"><img src="https://img.shields.io/github/stars/blackvvine/drive-deep-copy" alt="Stars Badge"/></a>
<a href="https://github.com/blackvvine/drive-deep-copy/network/members"><img src="https://img.shields.io/github/forks/blackvvine/drive-deep-copy" alt="Forks Badge"/></a>
<a href="https://github.com/blackvvine/drive-deep-copy/pulls"><img src="https://img.shields.io/github/issues-pr/blackvvine/drive-deep-copy" alt="Pull Requests Badge"/></a>
<a href="https://github.com/blackvvine/drive-deep-copy/issues"><img src="https://img.shields.io/github/issues/blackvvine/drive-deep-copy" alt="Issues Badge"/></a>
<a href="https://github.com/blackvvine/drive-deep-copy/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/blackvvine/drive-deep-copy?color=2b9348"></a>
<a href="https://github.com/blackvvine/drive-deep-copy/blob/master/LICENSE"><img src="https://img.shields.io/github/license/blackvvine/drive-deep-copy?color=2b9348" alt="License Badge"/></a>


A tiny recursive directory copy script for Google Drive

## Why

Google Drive no longer has the directory copy function, which is very useful when you want 
to back up frequently changing content stored on your shared drives. Existing solutions like
[gdrive-copy](https://github.com/ericyd/gdrive-copy) either require you to trust their 
demo launch with a token that gives them unlimited read-write access to every file in your 
drive, or make you deploy an app using [clasp](https://github.com/google/clasp) which is 
overkill for such a simple task.

## Setup

```
pip install virtualenv
python -m virtualenv venv -p /usr/bin/python3
. venv/bin/activate 
pip install requirements.txt
```

## Usage

1. Acquire your `credentials.json` file by following the [official guide](https://bit.ly/credjson)

2. Get your source and destination directory's UID from the address bar, when you open them in 
Google Drive web UI

3. Run the script:
```
python deepcopy.py <source> <destination> [--cred credentials.json (optional)] [--token token.json (optional)]
```


