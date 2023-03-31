wget -P /tmp https://dl.vndb.org/dump/vndb-db-latest.tar.zst
zstd -d --rm /tmp/vndb-db-latest.tar.zst
tar -x --directory="$1" --file=/tmp/vndb-db-latest.tar db/chars db/chars_vns db/staff_alias TIMESTAMP db/vn db/vn_titles
rm /tmp/vndb-db-latest.tar
