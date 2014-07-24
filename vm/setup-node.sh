echo "============== INSTALLING NODE DEPENDENCIES"
add-apt-repository ppa:chris-lea/node.js -y
apt-get update -y > /dev/null
apt-get install nodejs -y
