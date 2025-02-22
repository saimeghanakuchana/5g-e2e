#!/bin/bash
set -ex
BINDIR=`dirname $0`
source $BINDIR/common.sh

update_udhcpc_script () {
    sudo cp $BINDIR/default.script /etc/udhcpc/default.script
    sudo chmod +x /etc/udhcpc/default.script
}

install_ue_deps () {
    sudo apt update && sudo apt install -y --no-install-recommends \
      iperf3 \
      python3-pip \
      python3-zmq
    sudo pip3 install -r $BINDIR/requirements.txt
}

install_ue_services () {
  python_scripts=$(ls $BINDIR/*.py)
  for script in $python_scripts; do
      sudo cp $script $SRCDIR
  done
  services=$(ls $SERVICESDIR/*.service)
  for service in $services; do
      sudo cp $service /etc/systemd/system
      sudo systemctl daemon-reload
      sudo systemctl enable $(basename $service)
      sudo systemctl restart $(basename $service)
  done
}

airplane_mode_ue
maybe_add_quectel_cm
update_quectel_cm
update_udhcpc_script
install_ue_deps
install_ue_services
