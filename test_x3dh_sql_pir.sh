if [[ "$OSTYPE" == "darwin"* ]]; then
  mockusbfolder1=/Users/setup/repos/olibachi/testenv/mockusb/
  mockusbfolder2=/Users/setup/repos/olibachi/testenv/mockusb2/
  mockusbfolder3=/Users/setup/repos/olibachi/testenv/mockusb3/
  mockusbfolder4=/Users/setup/repos/olibachi/testenv/mockusb4/
  testenvironment=/Users/setup/repos/olibachi/testenv
else
  mockusbfolder1=/home/user/olibachi/testenv/mockusb/
  mockusbfolder2=/home/user/olibachi/testenv/mockusb2/
  mockusbfolder3=/home/user/olibachi/testenv/mockusb3/
  mockusbfolder4=/home/user/olibachi/testenv/mockusb4/
  testenvironment=/home/user/olibachi/testenv
fi

function initialise_user() {
  cd $testenvironment/$1
  python3 obfuscated_retrieval/BACnet/utils/feed_control.py cli -n $1 &
  LASTPID=$!
  sleep 0.6; kill $LASTPID
  python3 obfuscated_retrieval/BACnet/utils/clisneakernet.py $2 $1 -1
  cd ..
  cd ..
}
function go_to_env() {
  cd $testenvironment/$1
}
function do_feedcontrol_and_sneakernet_for_user() {
  python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $2 $1 -1
  python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
  LASTPID=$!
  sleep 5.0 ; kill $LASTPID
  python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $2 $1 -1
}
function do_sneakernet() {
  python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $2 $1 -1
}

initialise_user "user1" "$mockusbfolder1"
initialise_user "user2" "$mockusbfolder1"
#At this point, the master feed information for user1 and user2 has been synced on mockusbfolder1
initialise_user "user2" "$mockusbfolder2"
initialise_user "user4" "$mockusbfolder2"
#At this point, the master feed information for user2 and user4 has been synced on mockusbfolder2
initialise_user "user1" "$mockusbfolder3"
initialise_user "user3" "$mockusbfolder3"
#At this point the master feed information for user1 and user3 has been synced on mockusbfolder3
initialise_user "user3" "$mockusbfolder4"
initialise_user "user4" "$mockusbfolder4"
#At this point the master feed information for user3 and user4 has been synced on mockusbfolder4

go_to_env "user1"; do_sneakernet "user1" "$mockusbfolder1"
python3 main.py <<EOD
contact
1
EOD
do_sneakernet "user1" "$mockusbfolder1"

go_to_env "user2"; do_feedcontrol_and_sneakernet_for_user "user2" "$mockusbfolder1"
python3 main.py <<EOD
read-pkb
EOD
do_sneakernet "user2" "$mockusbfolder1"

go_to_env "user1"; do_feedcontrol_and_sneakernet_for_user "user1" "$mockusbfolder1"
python3 main.py <<EOD
read-res-pkb
EOD
do_sneakernet "user1" "$mockusbfolder1"

go_to_env "user2"; do_feedcontrol_and_sneakernet_for_user "user2" "$mockusbfolder1"
python3 main.py <<EOD
db-schemata
EOD
do_sneakernet "user2" "$mockusbfolder1"

go_to_env "user1"; do_feedcontrol_and_sneakernet_for_user "user1" "$mockusbfolder1"
python3 main.py <<EOD
decrypt-pir
EOD
python3 main.py <<EOD
pir
1
ownership
Physician_Profile_ID
Physician_First_Name
=
Nicole
3200
EOD
do_sneakernet "user1" "$mockusbfolder1"

go_to_env "user2"; do_feedcontrol_and_sneakernet_for_user "user2" "$mockusbfolder1"
python3 main.py <<EOD
decrypt-pir
EOD
do_sneakernet "user2" "$mockusbfolder1"
do_sneakernet "user2" "$mockusbfolder1"

go_to_env "user1"; do_feedcontrol_and_sneakernet_for_user "user1" "$mockusbfolder1"
do_feedcontrol_and_sneakernet_for_user "user1" "$mockusbfolder1"
python3 main.py <<EOD
read-res-pir
EOD
do_sneakernet "user1" "$mockusbfolder1"
