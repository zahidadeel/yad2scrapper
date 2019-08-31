sudo apt update -y
sudo apt upgrade -y
sudo apt install -y python3-dev python3-pip
sudo apt install -y firefox
sudo -H pip3 install -U -r requirements.txt
sudo cp -avf geckodriver /usr/bin/