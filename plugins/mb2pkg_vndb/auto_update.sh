wget -P /tmp https://dl.vndb.org/dump/vndb-db-latest.tar.zst
zstd -d --rm /tmp/vndb-db-latest.tar.zst
tar -xf /tmp/vndb-db-latest.tar db/chars db/chars_vns db/staff_alias TIMESTAMP db/vn db/vn_titles -C "$1"
rm /tmp/vndb-db-latest.tar
