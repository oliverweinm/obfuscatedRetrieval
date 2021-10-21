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
  sleep 0.5; kill $LASTPID
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
  sleep 3.5 ; kill $LASTPID
  python3 obfuscated_retrieval/BACnet/utils/clisneakernet.py $2 $1 -1
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
echo "main1"
python3 main.py <<EOD
contact
1
EOD
do_sneakernet "user1" "$mockusbfolder1"

go_to_env "user2"; do_feedcontrol_and_sneakernet_for_user "user2" "$mockusbfolder1"
echo "main2"
python3 main.py <<EOD
read-pkb
EOD
do_sneakernet "user2" "$mockusbfolder1"

go_to_env "user1"; do_feedcontrol_and_sneakernet_for_user "user1" "$mockusbfolder1"
echo "main3"
python3 main.py <<EOD
read-res-pkb
EOD
do_sneakernet "user1" "$mockusbfolder1"

go_to_env "user2"; do_feedcontrol_and_sneakernet_for_user "user2" "$mockusbfolder1"
echo "main4"
python3 main.py <<EOD
db-schemata
EOD
do_sneakernet "user2" "$mockusbfolder1"

go_to_env "user1"; do_feedcontrol_and_sneakernet_for_user "user1" "$mockusbfolder1"
echo "main5"
python3 main.py <<EOD
decrypt-pir
EOD
echo "AT THIS POINT X3DH BETWEEN USER1 AND USER2 IS COMPLETE AND CONFIRMED"

go_to_env "user2"; do_sneakernet "user2" "$mockusbfolder2"
echo "main6"
python3 main.py <<EOD
contact
2
EOD
do_sneakernet "user2" "$mockusbfolder2"

go_to_env "user4"; do_feedcontrol_and_sneakernet_for_user "user4" "$mockusbfolder2"
echo "main7"
python3 main.py <<EOD
read-pkb
EOD
do_sneakernet "user4" "$mockusbfolder2"

go_to_env "user2"; do_feedcontrol_and_sneakernet_for_user "user2" "$mockusbfolder2"
echo "main8"
python3 main.py <<EOD
read-res-pkb
EOD
do_sneakernet "user2" "$mockusbfolder2"

go_to_env "user4"; do_feedcontrol_and_sneakernet_for_user "user4" "$mockusbfolder2"
echo "main9"
python3 main.py <<EOD
db-schemata
EOD
do_sneakernet "user4" "$mockusbfolder2"

go_to_env "user2"; do_feedcontrol_and_sneakernet_for_user "user1" "$mockusbfolder2"
echo "main10"
python3 main.py <<EOD
decrypt-pir
EOD
echo "AT THIS POINT X3DH BETWEEN USER1 AND USER2 IS COMPLETE AND CONFIRMED"
echo "AT THIS POINT X3DH BETWEEN USER2 AND USER4 IS COMPLETE AND CONFIRMED"
go_to_env "user1"; do_sneakernet "user1" "$mockusbfolder3"
echo "main11"
python3 main.py <<EOD
contact
2
EOD
do_sneakernet "user1" "$mockusbfolder3"

go_to_env "user3"; do_feedcontrol_and_sneakernet_for_user "user3" "$mockusbfolder3"
echo "main12"
python3 main.py <<EOD
read-pkb
EOD
do_sneakernet "user3" "$mockusbfolder3"

go_to_env "user1"; do_feedcontrol_and_sneakernet_for_user "user1" "$mockusbfolder3"
echo "main13"
python3 main.py <<EOD
read-res-pkb
EOD
do_sneakernet "user1" "$mockusbfolder3"

go_to_env "user3"; do_feedcontrol_and_sneakernet_for_user "user3" "$mockusbfolder3"
echo "main14"
python3 main.py <<EOD
db-schemata
EOD
do_sneakernet "user3" "$mockusbfolder3"

go_to_env "user1"; do_feedcontrol_and_sneakernet_for_user "user1" "$mockusbfolder3"
echo "main15"
python3 main.py <<EOD
decrypt-pir
EOD
echo "AT THIS POINT X3DH BETWEEN USER1 AND USER2 IS COMPLETE AND CONFIRMED"
echo "AT THIS POINT X3DH BETWEEN USER2 AND USER4 IS COMPLETE AND CONFIRMED"
echo "AT THIS POINT X3DH BETWEEN USER1 AND USER3 IS COMPLETE AND CONFIRMED"
go_to_env "user3"; do_sneakernet "user3" "$mockusbfolder4"
echo "main16"
python3 main.py <<EOD
contact
3
EOD
do_sneakernet "user3" "$mockusbfolder4"

go_to_env "user4"; do_feedcontrol_and_sneakernet_for_user "user4" "$mockusbfolder4"
echo "main17"
python3 main.py <<EOD
read-pkb
EOD
do_sneakernet "user4" "$mockusbfolder4"

go_to_env "user3"; do_feedcontrol_and_sneakernet_for_user "user3" "$mockusbfolder4"
echo "main18"
python3 main.py <<EOD
read-res-pkb
EOD
do_sneakernet "user3" "$mockusbfolder4"

go_to_env "user4"; do_feedcontrol_and_sneakernet_for_user "user4" "$mockusbfolder4"
echo "main19"
python3 main.py <<EOD
db-schemata
EOD
do_sneakernet "user4" "$mockusbfolder4"

go_to_env "user3"; do_feedcontrol_and_sneakernet_for_user "user3" "$mockusbfolder4"
echo "main20"
python3 main.py <<EOD
decrypt-pir
EOD
echo "AT THIS POINT X3DH BETWEEN USER1 AND USER2 IS COMPLETE AND CONFIRMED"
echo "AT THIS POINT X3DH BETWEEN USER2 AND USER4 IS COMPLETE AND CONFIRMED"
echo "AT THIS POINT X3DH BETWEEN USER1 AND USER3 IS COMPLETE AND CONFIRMED"
echo "AT THIS POINT X3DH BETWEEN USER3 AND USER4 IS COMPLETE AND CONFIRMED"

go_to_env "user1";
echo "main21"
python3 main.py <<EOD
pir
1
ownership
Physician_Profile_ID
Physician_First_Name
=
'Nicole'
3200
EOD

do_sneakernet "user1" "$mockusbfolder1"
do_sneakernet "user1" "$mockusbfolder3"

go_to_env "user2"; do_feedcontrol_and_sneakernet_for_user "user2" "$mockusbfolder1"
echo "main22"
python3 main.py <<EOD
decrypt-pir
EOD
do_sneakernet "user2" "$mockusbfolder2"

go_to_env "user3"; do_feedcontrol_and_sneakernet_for_user "user3" "$mockusbfolder3"
echo "main23"
python3 main.py <<EOD
decrypt-pir
EOD
do_sneakernet "user3" "$mockusbfolder4"
echo "AT THIS POINT USER2 AND USER3 HAVE RECEIVED THE PIR QUERIES FROM USER1 AND PROCESSED THEM."

go_to_env "user4"; do_feedcontrol_and_sneakernet_for_user "user4" "$mockusbfolder2"
echo "main24"
python3 main.py <<EOD
decrypt-pir
EOD
do_sneakernet "user4" "$mockusbfolder2"

do_feedcontrol_and_sneakernet_for_user "user4" "$mockusbfolder4"
echo "main25"
python3 main.py <<EOD
decrypt-pir
EOD
do_sneakernet "user4" "$mockusbfolder4"
echo "AT THIS POINT USER4 HAS RECEIVED THE PIR QUERIES FROM USER2 AND USER3 AND PROCESSED THEM."

go_to_env "user2"; do_feedcontrol_and_sneakernet_for_user "user2" "$mockusbfolder2"
echo "main26"
python3 main.py <<EOD
read-res-pir
EOD
do_sneakernet "user2" "$mockusbfolder1"

echo "main27"
go_to_env "user3"; do_feedcontrol_and_sneakernet_for_user "user3" "$mockusbfolder4"
python3 main.py <<EOD
read-res-pir
EOD
do_sneakernet "user3" "$mockusbfolder3"

echo "AT THIS POINT USER2 AND USER3 HAVE RECEIVED THE RESPONSE KEY BUNDLE AND SENT THEM TO USER1."

go_to_env "user1"; do_feedcontrol_and_sneakernet_for_user "user1" "$mockusbfolder1"
echo "main28"
python3 main.py <<EOD
read-res-pir
EOD
#do_sneakernet "user1" "$mockusbfolder1"

do_feedcontrol_and_sneakernet_for_user "user1" "$mockusbfolder3"
echo "main29"
python3 main.py <<EOD
read-res-pir
EOD
#do_sneakernet "user1" "$mockusbfolder1"
