#!/bin/zsh

update_version_regex="(\S+)\s(\S*\s->\s\S.*)"

date=$(date +'%Y-%m-%d_%H-%M')
log_dir=${0%/*}/brew_upgrade_logs
log_file=$log_dir/brew_upgrade_$date.log

if [ ! -d "$log_dir" ]; then
  mkdir -p "$log_dir"
fi

touch "$log_file"
/opt/homebrew/bin/brew upgrade >"$log_file" 2>&1

msg=$(/usr/local/bin/pcregrep -o1 -o2 --om-separator=' ' "$update_version_regex" "$log_file")

if [[ -n $msg ]]; then
  /usr/local/bin/noti -t "Package(s) updated" -m "$msg"
fi
