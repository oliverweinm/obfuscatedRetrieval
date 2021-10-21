function update_folder() {
  rm -rf testenv/$1/*
  cp -r obfuscated_retrieval testenv/$1
  mkdir testenv/$1/public_key
  mkdir testenv/$1/encryption_key_files
  cp main.py testenv/$1
}

echo "$OSTYPE"
if [[ "$OSTYPE" == "darwin"* ]]; then
  rm /Users/setup/repos/olibachi/testenv/mockusb/*
  rm /Users/setup/repos/olibachi/testenv/mockusb2/*
  rm /Users/setup/repos/olibachi/testenv/mockusb3/*
  rm /Users/setup/repos/olibachi/testenv/mockusb4/*
else
  rm /home/user/olibachi/testenv/mockusb/*
  rm /home/user/olibachi/testenv/mockusb2/*
  rm /home/user/olibachi/testenv/mockusb3/*
  rm /home/user/olibachi/testenv/mockusb4/*
fi

cd ..
update_folder "user1"
update_folder "user2"
update_folder "user3"
update_folder "user4"

cp *.db testenv/user4
