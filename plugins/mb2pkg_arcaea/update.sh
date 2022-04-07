# Requirements: apt-get install jq aria2
#
# Usage:
# 1. modify $temp_dir, this is a folder to store downloaded apk and unpacked files,
#    it will be automatically **created** if it does not exist.
#    It will be automatically **deleted** after the script is executed.
# 2. modify $save_dir, this is the parent folder of the "songs" folder and the "char" folder.
# 3. modify $local_version_file, this is a file to record the local version (Optional).
# 4. modify $keep_or_remove, select how to parse the song cover filename (keep or remove "dl_").


readonly webapi_url="https://webapi.lowiro.com/webapi/serve/static/bin/arcaea/apk"
readonly json_value_url=".value.url"
readonly json_value_version=".value.version"

readonly local_version_file="/tmp/local_version"
readonly temp_dir="/tmp/arcaea"
readonly save_dir="/root/mokabot2/plugins/mb2pkg_arcaea/res/arcaea_draw"
readonly keep_or_remove="remove"

readonly green_font_prefix="\033[32m"
readonly yellow_font_prefix="\033[33m"
readonly red_font_prefix="\033[31m"
readonly font_color_suffix="\033[0m"

readonly info="[${green_font_prefix}info${font_color_suffix}]"
readonly warn="[${yellow_font_prefix}warn${font_color_suffix}]"
readonly error="[${red_font_prefix}error${font_color_suffix}]"


# read local version from local_version file
if [ -e "${local_version_file}" ]; then
  read -r local_version < "${local_version_file}"
else
  local_version="unknown"
fi

# curl the remote version info
webapi_apk_response=$(curl -L "${webapi_url}")
remote_version=$(jq -r "${json_value_version}" <<< "${webapi_apk_response}")

# if remote != local then update else exit 0
echo -e "${info}Local Arcaea apk version is ${local_version}."
echo -e "${info}Remote Arcaea apk version is ${remote_version}."

if test "${remote_version}" = "${local_version}"; then
  echo -e "${info}Arcaea is already the latest version."
  exit 0
else
  echo -e "${warn}Need update, Arcaea ${remote_version} will be downloaded."
fi

# aria2c and unzip the apk
mkdir -p $temp_dir
apk_url=$(jq -r "${json_value_url}" <<< "${webapi_apk_response}")
aria2c --dir="${temp_dir}" --out="${remote_version}.apk" --max-connection-per-server=16 --split=16 --min-split-size=1M "${apk_url}"
# if apk is not downloaded then exit 1 else continue
if [ -e "${temp_dir}/${remote_version}.apk" ]; then
  echo -e "${info}Download complete, please wait for unzip ..."
else
  echo -e "${error}Download failed, please check your network."
  exit 1
fi
unzip -oq "${temp_dir}/${remote_version}.apk" -d "${temp_dir}/${remote_version}"
# if apk cannot unzip then exit 1 else continue
if [ -d "${temp_dir}/${remote_version}/assets" ]; then
  echo -e "${info}Unzip complete, now moving files ..."
else
  echo -e "${error}Unzip failed, bad file."
  exit 1
fi

# mv assets/char/* > save_dir/char/$1
mkdir -p "${save_dir}/char"
mv -f "${temp_dir}/${remote_version}/assets/char/"* "${save_dir}/char/"
echo -e "${info}Successfully moved character files."

# mv assets/songs/*/base.jpg > save_dir/songs/$1.jpg
mkdir -p "${save_dir}/songs"
file_list=$(ls "${temp_dir}/${remote_version}/assets/songs")
for song_name in $file_list; do
  # ignore the useless files
  if [[ "${song_name}" =~ (packlist|songlist|unlocks|pack) ]]; then
    continue
  fi
  # select how to parse the song cover filename
  if test "${keep_or_remove}" = "keep"; then  # keep "dl_" in filename (for mokabot)
    mv -f "${temp_dir}/${remote_version}/assets/songs/${song_name}/base.jpg" "${save_dir}/songs/${song_name}.jpg"
  elif test "${keep_or_remove}" = "remove"; then  # remove "dl_" in filename (for AUA)
    mv -f "${temp_dir}/${remote_version}/assets/songs/${song_name}/base.jpg" "${save_dir}/songs/${song_name##*_}.jpg"
  fi
done
echo -e "${info}Successfully moved song cover files."

# only for mokabot
# mv assets/songs/songlist > save_dir/../songmeta/songlist.json
# mv assets/songs/packlist > save_dir/../songmeta/packlist.json
mkdir -p "${save_dir}/../songmeta"
mv -f "${temp_dir}/${remote_version}/assets/songs/songlist" "${save_dir}/../songmeta/songlist.json"
mv -f "${temp_dir}/${remote_version}/assets/songs/packlist" "${save_dir}/../songmeta/packlist.json"
echo -e "${info}Successfully moved song meta files."

# overwrite the local_version file
echo "$remote_version" > $local_version_file
read -r local_version < "${local_version_file}"
echo -e "${info}Update complete, local version is ${local_version} now."

# rm the temp files
rm -r "${temp_dir}"
echo -e "${info}Successfully removed temp files."

echo -e "${info}Bye."
