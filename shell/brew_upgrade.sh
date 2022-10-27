#!/usr/bin/env zsh -l

# update_version_regex="Upgrading\s(.*)\s(\S*\s->\s\S.*)"
update_version_regex="(\S+)\s(\S*\s->\s\S.*)"
update_successful_regex="(.*)\swas\ssuccessfully\supgraded"

# source /etc/profile

date=`date +'%Y-%m-%d_%H-%M'`
touch /Users/arnewohletz/MyDevelopmentProjects/scripts/shell/brew_upgrade_$date.tmp
tmp_file=/Users/arnewohletz/MyDevelopmentProjects/scripts/shell/brew_upgrade_$date.tmp
script -q $tmp_file brew upgrade >/dev/null

match=$(pcregrep -o1 $update_version_regex $tmp_file)
UPGRADE_APPS=($(echo $match))

match=$(pcregrep -o1 -o2 --om-separator=' ' $update_version_regex $tmp_file)
UPGRADE_APP_MESSAGES=($(echo $match | tr " " "_"))

# match=($(pcregrep -o1 $update_successful_regex $tmp_file))
# UPGRADE_APP_SUCCESSFUL=($(echo $match))

ITER=1
msg=""

for val in "${UPGRADE_APPS[@]}"
do
  msg+="$(echo $UPGRADE_APP_MESSAGES[$ITER] | tr "_" " ")"
  # if [[ $UPGRADE_APP_SUCCESSFUL[$ITER] = $UPGRADE_APPS[$ITER] ]]
  # then
  #   msg+="$(echo $UPGRADE_APP_MESSAGES[$ITER] | tr "_" " ")"
  # else
  #   msg+="$(echo "FAILED UPDATE:" $UPGRADE_APPS[$ITER] | tr "_" " ")"
  # msg+=";"
  # fi
((ITER++))
done

if [[ ! -z $msg ]]
then
  noti -t "Package(s) updated" -m "$msg"
# else
#   say "I did not hit her, it's not true! It's bullshit! I did not hit her! I did not. Oh hi, Mark."
fi
