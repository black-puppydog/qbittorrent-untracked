import argparse
import os
import sys
from pathlib import Path
from pprint import pformat

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Checks a folder for files that are currently "
                                     "*not* tracked by qBittorrent. This is useful "
                                     "for detecting dead files that could be deleted.")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-u", "--username", default="admin")
    parser.add_argument("--password", default=None)
    parser.add_argument("--torrent-root-local", default=None)
    parser.add_argument("torrent_root_server")
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
print(file=sys.stderr)

torrent_root_server = Path(args.torrent_root_server)
torrent_root_local = Path(args.torrent_root_local)

# instantiate a Client using the appropriate WebUI configuration
import qbittorrentapi
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
        # if "name" not in file_info:
        #     print(pformat(dict(torrent_info)), file=sys.stderr)
        #     print(pformat(dict(file_info)), file=sys.stderr)
        file_path = torrent_path / file_info["name"]
        tracked_files.add(file_path.relative_to(torrent_root_server).as_posix())
print(f"{len(tracked_files):7} files currently tracked.", file=sys.stderr)

print("Beginning file system scan...", file=sys.stderr)
print(file=sys.stderr)
untracked = 0
total_seen = 0
for fname in tqdm(torrent_root_local.glob("**/*")):
    total_seen += 1
    relative = fname.relative_to(torrent_root_local)
    if fname not in tracked_files:
        print(fname.as_posix())
        untracked += 1
print(file=sys.stderr)
print(f"{total_seen:7} files seen locally.", file=sys.stderr)
print(f"{untracked:7} files untracked.", file=sys.stderr)
