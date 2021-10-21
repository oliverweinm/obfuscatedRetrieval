if [[ "$OSTYPE" == "darwin"* ]]; then
  mockusbfolder=/Users/setup/repos/olibachi/testenv/mockusb/
  testenvironment=/Users/setup/repos/olibachi/testenv
else
  mockusbfolder=/home/user/olibachi/testenv/mockusb/
  testenvironment=/home/user/olibachi/testenv
fi

function execute_user() {
  #echo $testenvironment/$1
  cd $testenvironment/$1
  python3 obfuscated_retrieval/BACnet/utils/feed_control.py cli -n $1 &
  LASTPID=$!
  sleep 0.01; kill $LASTPID
  python3 obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder $1 -1
  cd ..
  cd ..
}

execute_user "user1"
execute_user "user2"

cd $testenvironment/user1
python3 obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user1 -1
python3 main.py <<EOD
contact
1
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user1 -1

cd $testenvironment/user2
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user2 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 5.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user2 -1
python3 main.py <<EOD
read-pkb
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user2 -1

cd $testenvironment/user1
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user1 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 7.0 ; kill $LASTPID

python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user1 -1

python3 main.py <<EOD
read-res-pkb
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user1 -1

cd $testenvironment/user2
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user2 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &
LASTPID=$!
sleep 7.0 ; kill $LASTPID

python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user2 -1
python3 main.py <<EOD
db-schemata
EOD

python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user2 -1


cd $testenvironment/user1
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user1 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &

LASTPID=$!
sleep 10.0 ; kill $LASTPID
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user1 -1
python3 main.py <<EOD
decrypt-pir
EOD

echo "HERE BE DRAGONS"
echo "HERE BE DRAGONS"
echo "HERE BE DRAGONS"
echo "HERE BE DRAGONS"
echo "HERE BE DRAGONS"
python3 main.py <<EOD
pir
1
table
column
columnName
operator
value
EOD
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user1 -1

cd $testenvironment/user2
python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user2 -1
python3 ./obfuscated_retrieval/BACnet/utils/feed_control.py cli -ta &

LASTPID=$!
sleep 10.0 ; kill $LASTPID

python3 ./obfuscated_retrieval/BACnet/utils/clisneakernet.py $mockusbfolder user2 -1
python3 main.py <<EOD
decrypt-pir
EOD
