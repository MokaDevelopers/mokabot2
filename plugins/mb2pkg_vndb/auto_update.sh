wget -P /tmp https://dl.vndb.org/dump/vndb-db-latest.tar.zst
zstd -d --rm /tmp/vndb-db-latest.tar.zst
tar -xf /tmp/vndb-db-latest.tar plugins/mb2pkg_vndb/res/db/chars plugins/mb2pkg_vndb/res/db/chars_vns plugins/mb2pkg_vndb/res/db/staff_alias plugins/mb2pkg_vndb/res/TIMESTAMP plugins/mb2pkg_vndb/res/db/vn plugins/mb2pkg_vndb/res/db/vn_titles -C "$1"
rm /tmp/vndb-db-latest.tar
