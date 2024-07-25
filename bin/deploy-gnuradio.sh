#!/bin/bash
set -ex
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

# install required packages for gnuradio/gnuradio-companion/uhd
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    gir1.2-gtk-3.0 \
    gnuradio \
    gobject-introspection \
    python3-gi \
    uhd-host

sudo /usr/libexec/uhd/utils/uhd_images_downloader.py
