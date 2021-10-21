if [[ "$OSTYPE" == "darwin"* ]]; then
  mockusbfolder1=/Users/setup/repos/olibachi/testenv/mockusb/
  mockusbfolder2=/Users/setup/repos/olibachi/testenv/mockusb2/
  mockusbfolder3=/Users/setup/repos/olibachi/testenv/mockusb3/
  mockusbfolder4=/Users/setup/repos/olibachi/testenv/mockusb4/
  testenvironment=/Users/setup/repos/olibachi/testenv
else
  mockusbfolder=/home/user/olisbachelor/testenv/mockusb/
  testenvironment=/home/user/olisbachelor/testenv
fi

function execute_user() {
  #echo $testenvironment/$1
  cd $testenvironment/$1
  python3 obfuscated_retrieval/BACnet/utils/feed_control.py cli -n $1 &
  LASTPID=$!
  sleep 0.1; kill $LASTPID
  python3 obfuscated_retrieval/BACnet/utils/clisneakernet.py $2 $1 -1
  cd ..
  cd ..
}

#              user2
#            /           \
#          / mocksub1      \ mockusb2
#        /                    \
# user1                        user4
#        \                     /
#          \ mockusb3     / mockusb4
#             \        /
#              user3

execute_user "user1" "$mockusbfolder1"
execute_user "user2" "$mockusbfolder1"
#At this point, the master feed information for user1 and user2 has been synced on mockusbfolder1
execute_user "user2" "$mockusbfolder2"
execute_user "user4" "$mockusbfolder2"
#At this point, the master feed information for user2 and user4 has been synced on mockusbfolder2
execute_user "user1" "$mockusbfolder3"
execute_user "user3" "$mockusbfolder3"
#At this point the master feed information for user2
execute_user "user3" "$mockusbfolder4"
execute_user "user4" "$mockusbfolder4"

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

cd $testenvironment/user4

python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user4 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 5.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user4 -1

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

cd $testenvironment/user4

python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user4 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 5.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user4 -1
python3 main.py <<EOD
read-pkb
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder2 user4 -1

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

cd $testenvironment/user3
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder3 user3 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 5.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder3 user3 -1

cd $testenvironment/user1
python3 obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder3 user1 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 5.0 ; kill $LASTPID
python3 main.py <<EOD
contact
2
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder3 user1 -1

cd $testenvironment/user3
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder3 user3 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 5.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder3 user3 -1
python3 main.py <<EOD
read-pkb
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder3 user3 -1

echo "This is where shit hits the fan"
cd $testenvironment/user1
python3 obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder3 user1 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 5.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder3 user1 -1
python3 main.py <<EOD
read-res-pkb
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder3 user1 -1
