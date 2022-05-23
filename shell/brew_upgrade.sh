#!/bin/zsh

update_version_regex="Upgrading (.*)\s(\S*\s->\s\S.*)"
update_successful_regex="(.*)\swas successfully upgraded"

OUTPUT_MOCK="Upgrading RandomApp 1.0.1 -> 1.0.2
blablabla
RandomApp was successfully upgraded!
blablabla
Upgrading ImportantApp 3.1 -> 3.2
blablabla
ImportantApp was successfully upgraded!
blablabla
Upgrading WillFailApp 0.1 -> 0.2
blablabla
WillFailApp update failed!
"

OUTPUT=`brew upgrade` 2>&1 | tee brew_upgrade.tmp
# echo "$OUTPUT" > brew_upgrade.tmp

match=$(pcregrep -o1 $update_version_regex brew_upgrade.tmp)
UPGRADE_APPS=($(echo $match))

match=$(pcregrep -o1 -o2 --om-separator=' ' $update_version_regex brew_upgrade.tmp)
UPGRADE_APP_MESSAGES=($(echo $match | tr " " "_"))

match=($(pcregrep -o1 $update_successful_regex brew_upgrade.tmp))
UPGRADE_APP_SUCCESSFUL=($(echo $match))

ITER=1
msg=""

for val in "${UPGRADE_APPS[@]}"
do
  if [[ $UPGRADE_APP_SUCCESSFUL[$ITER] = $UPGRADE_APPS[$ITER] ]]
  then
    msg+="$(echo $UPGRADE_APP_MESSAGES[$ITER] | tr "_" " ")"
  else
    msg+="$(echo "FAILED UPDATE:" $UPGRADE_APPS[$ITER] | tr "_" " ")"
  msg+="; "
  fi
((ITER++))
done

if [[ ! -z $msg ]]
then
  noti -t "Package(s) updated" -m "$msg"
fi
