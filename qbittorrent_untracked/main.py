import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Checks a folder for files that are currently "
                                     "*not* tracked by qBittorrent. This is useful "
                                     "for detecting dead files that could be deleted.")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-u", "--username", default="admin")
    parser.add_argument("--password", default=None)
    args = parser.parse_args()
    if args.password is None:
        print("Trying to get password from environment variable QBITTORRENT_PASSWORD")
        args.password = os.environ.get("QBITTORRENT_PASSWORD", None)
        if args.password is None:
            print("Defaulting to 'adminadmin'")
            args.password = "adminadmin"

# instantiate a Client using the appropriate WebUI configuration
import qbittorrentapi
qbt_client = qbittorrentapi.Client(
    **vars(args)
)


# the Client will automatically acquire/maintain a logged-in state
# in line with any request. therefore, this is not strictly necessary;
# however, you may want to test the provided login credentials.
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

# display qBittorrent info
print(f'qBittorrent: {qbt_client.app.version}')
print(f'qBittorrent Web API: {qbt_client.app.web_api_version}')
for k,v in qbt_client.app.build_info.items(): print(f'{k}: {v}')
