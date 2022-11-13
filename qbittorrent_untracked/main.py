#!/usr/bin/env python3.9

import argparse
import os
import sys
from pathlib import Path
from pprint import pformat
from collections import defaultdict

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Checks a folder for files that are currently "
                                     "*not* tracked by qBittorrent. This is useful "
                                     "for detecting dead files that could be deleted.")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-u", "--username", default="admin")
    parser.add_argument("--password", default=None)
    parser.add_argument("--torrent-root-local", default=None)
    parser.add_argument("-x", "--exclude", action="append", type=Path,
                        help=("Files and folders to ignore when finding untracked "
                              "files. These can be absolute, or relative to the local "
                              "torrent root."))
    parser.add_argument("torrent_root_server", type=Path)
    args = parser.parse_args()
    if args.torrent_root_local is None:
        args.torrent_root_local = args.torrent_root_server
    if args.password is None:
        print("Trying to get password from environment variable QBITTORRENT_PASSWORD",
              file=sys.stderr)
        args.password = os.environ.get("QBITTORRENT_PASSWORD", None)
        if args.password is None:
            print("Defaulting to 'adminadmin'", file=sys.stderr)
            args.password = "adminadmin"
    args.torrent_root_local = Path(args.torrent_root_local)
    args.exclude = [
        e if e.is_absolute() else args.torrent_root_local / e
        for e in args.exclude
    ]
print(file=sys.stderr)


# instantiate a Client using the appropriate WebUI configuration
import qbittorrentapi
from tqdm import tqdm

qbt_client = qbittorrentapi.Client(
    host=args.host,
    port=args.port,
    username=args.username,
    password=args.password,
)


# the Client will automatically acquire/maintain a logged-in state
# in line with any request. therefore, this is not strictly necessary;
# however, you may want to test the provided login credentials.
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e, file=sys.stderr)

# display qBittorrent info
print(f'qBittorrent: {qbt_client.app.version}', file=sys.stderr)
print(f'qBittorrent Web API: {qbt_client.app.web_api_version}', file=sys.stderr)
for k,v in qbt_client.app.build_info.items(): print(f'{k}: {v}', file=sys.stderr)
print(file=sys.stderr)

all_info = qbt_client.torrents.info.all()
tracked_files = set()
for torrent_info in all_info:
    torrent_path = Path(torrent_info["save_path"])
    for file_info in torrent_info.files:
        file_path = torrent_path / file_info["name"]
        tracked_files.add(file_path.relative_to(args.torrent_root_server).as_posix())

print(f"{len(tracked_files):7} files currently tracked.", file=sys.stderr)
print("Beginning file system scan...", file=sys.stderr)
print(file=sys.stderr)

untracked = list()
total_seen = 0

# this will hold all files as leaves, but also all folders in the local
# torrent root, and a value for each of them to see whether they only contain only
# untracked files. for the leaves, this is trivial: it's simply whether that file is
# tracked or not. for the folders, we build the values as we scan all the files.
contains_only_untracked_files = defaultdict(lambda: True)

def register_file(filename: Path, tracked: bool):
  contains_only_untracked_files[filename.as_posix()] = not tracked
  for folder in filename.parents:
    contains_only_untracked_files[folder] &= not tracked
    if folder == args.torrent_root_local:
      break

for fname in tqdm(args.torrent_root_local.glob("**/*")):
    if any(fname.is_relative_to(e) for e in args.exclude):
        continue
    if not fname.is_file():
        continue
    total_seen += 1
    relative = fname.relative_to(args.torrent_root_local).as_posix()
    if relative in tracked_files:
          register_file(fname, tracked=True)
    else:
          register_file(fname, tracked=False)
          untracked.append(fname)

print(file=sys.stderr)
print(f"{total_seen:7} files seen locally.", file=sys.stderr)
print(f"{len(untracked):7} files untracked.", file=sys.stderr)

def highest_untracked_parent(untracked_file: Path) -> Path:
    current = untracked_file
    current_contains_only_untracked = contains_only_untracked_files[current]
    assert current_contains_only_untracked, f"Weird result for {current}"
    while current != args.torrent_root_local:
        parent_contains_only_untracked = contains_only_untracked_files[current.parent]
        if not parent_contains_only_untracked:
            break
        current = current.parent
    return current.relative_to(args.torrent_root_local)

most_specific_files_and_folders = {highest_untracked_parent(filename) for filename
                                   in untracked}

for name in sorted(most_specific_files_and_folders):
    print(name)
