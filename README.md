# qbittorrent-untracked

A small helper script that finds all files in a folder that are currently *not* tracked
by qBittorrent. This is useful if you use e.g. the excellent [academic torrents][at]
or just create torrent files from your own data as a simple integrity safety.
Checking the dataset on disk against the torrent checksums quickly flags if any of the
files have been changed, or whether you stored intermediate files into the supposed
source-of-truth folder.

`qbittorrent-untracked` to the rescue!

`qbittorrent-untracked` connects directly to the qBittorrent web API using your admin
credentials, pulls the full list of files tracked in all torrents, and compares it to
the list of files actually found on disk. 
It then shows you all the files or folders that qBittorrent isn't aware of; these
should then be moved or deleted.

[at]: https://academictorrents.com/

## Example call:

```terminal
qbuntracked \
--host dataset-server.local \         # where you'd open your qBittorrent web UI
--torrent-root-local /nfs/datasets \  # where you mount your torrents *locally*
-x torrent_files \                    # exclude folder relative to torrent root
-x /nfs/datasets/untracked \          # exclude folder with absolute path
/mnt/pool/datasets                    # mount point of torrent folder on the server
```
