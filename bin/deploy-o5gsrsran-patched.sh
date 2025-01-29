#!/bin/bash
set -ex
BINDIR=`dirname $0`
SRCDIR=/var/tmp
ETCDIR=/local/repository/etc
SRS_PROJECT_REPO="https://github.com/srsRAN/srsRAN_Project"
COMMIT_HASH="5e6f50a202c6efa671d5b231d7c911dc6c3d86ed"
RELEASE_24_04_HASH="a15950301c5f3a1a166b79bb6c9ee901a4e8c2dd"

if [ -f $SRCDIR/srs-o5gs-setup-complete ]; then
  echo "setup already ran; not running again"
  exit 0
fi

# Get the emulab repo
while ! wget -qO - http://repos.emulab.net/emulab.key | sudo apt-key add -
do
    echo Failed to get emulab key, retrying
done

while ! sudo add-apt-repository -y http://repos.emulab.net/powder/ubuntu/
do
    echo Failed to get johnsond ppa, retrying
done

while ! sudo apt-get update
do
    echo Failed to update, retrying
done

# srsran dependencies
sudo apt-get install -y libuhd-dev uhd-host
sudo uhd_images_downloader
sudo apt-get install -y \
  cmake \
  make \
  gcc \
  g++ \
  iperf3 \
  pkg-config \
  libboost-dev \
  libfftw3-dev \
  libmbedtls-dev \
  libsctp-dev \
  libyaml-cpp-dev \
  libgtest-dev \
  numactl \
  ppp

# docker and wireshark/tshark
sudo add-apt-repository -y ppa:wireshark-dev/stable
echo "wireshark-common wireshark-common/install-setuid boolean false" | sudo debconf-set-selections
sudo apt update

sudo apt-get install -y \
  docker \
  docker-compose \
  software-properties-common \
  tshark \
  wireshark

cd $SRCDIR
git clone $SRS_PROJECT_REPO
cp -r srsRAN_Project srsRAN_Project_2404
cd srsRAN_Project
git checkout $COMMIT_HASH
git apply $ETCDIR/srsran/srsran-tdd.patch
mkdir build
cd build
cmake ../
make -j $(nproc)

echo configuring nodeb...
mkdir -p $SRCDIR/etc/srsran
cp -r $ETCDIR/srsran/* $SRCDIR/etc/srsran/
echo configuring nodeb... done.

echo configuring and starting open5gs container...
cd $SRCDIR/srsRAN_Project_2404
git checkout $RELEASE_24_04_HASH
git apply $ETCDIR/srsran/srsran-cn.patch
cp $ETCDIR/open5gs/subscriber_db.csv $SRCDIR/srsRAN_Project_2404/docker/open5gs/
cd $SRCDIR/srsRAN_Project_2404/docker/open5gs
sudo docker network create --subnet=10.53.0.0/16 open5gsnet
sudo docker build --target open5gs -t open5gs-docker .
sudo docker run --net open5gsnet --ip 10.53.1.2 --env-file open5gs.env --privileged --publish 9999:9999 -d open5gs-docker ./build/tests/app/5gc -c open5gs-5gc.yml
echo configuring and starting open5gs container... done.

touch $SRCDIR/srs-o5gs-setup-complete
