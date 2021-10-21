if [[ "$OSTYPE" == "darwin"* ]]; then
  mockusbfolder1=/Users/setup/repos/olibachi/testenv/mockusb/
  mockusbfolder2=/Users/setup/repos/olibachi/testenv/mockusb2/
  testenvironment=/Users/setup/repos/olibachi/testenv
else
  mockusbfolder=/home/user/olisbachelor/testenv/mockusb/
  testenvironment=/home/user/olisbachelor/testenv
fi

function execute_user_usb1() {
  #echo $testenvironment/$1
  cd $testenvironment/$1
  python3 obfuscated_retrieval/BACnet/utils/feed_control.py cli -n $1 &
  LASTPID=$!
  sleep 0.1; kill $LASTPID
  python3 obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder1 $1 -1
  cd ..
  cd ..
}

function execute_user_usb2() {
  #echo $testenvironment/$1
  cd $testenvironment/$1
  python3 obfuscated_retrieval/BACnet/utils/feed_control.py cli -n $1 &
  LASTPID=$!
  sleep 0.1; kill $LASTPID
  python3 obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 $1 -1
  cd ..
  cd ..
}

execute_user_usb1 "user1"
execute_user_usb1 "user2"
#At this point, the master feed information for user1 and user2 has been synced on mockusbfolder1
execute_user_usb2 "user2"
execute_user_usb2 "user3"
#At this point, the master feed information for user2 and user3 has been synced on mockusbfolder2

cd $testenvironment/user1
python3 obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder1 user1 -1
python3 main.py <<EOD
contact
1
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder1 user1 -1

cd $testenvironment/user2

python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder1 user2 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 5.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder1 user2 -1
python3 main.py <<EOD
read-pkb
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder1 user2 -1

cd $testenvironment/user1

python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder1 user1 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 7.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder1 user1 -1

python3 main.py <<EOD
read-res-pkb
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder1 user1 -1

cd $testenvironment/user3
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user3 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 5.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user3 -1

cd $testenvironment/user2
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user2 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 7.0 ; kill $LASTPID
python3 main.py <<EOD
contact
2
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user2 -1

cd $testenvironment/user3
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user3 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 5.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user3 -1
python3 main.py <<EOD
read-pkb
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user3 -1

cd $testenvironment/user2
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user2 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 5.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user2 -1
python3 main.py <<EOD
read-res-pkb
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user2 -1
