#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y \
  python3 \
  python3-pip \
  python3-bpfcc \
  bpfcc-tools \
  linux-headers-generic

if [[ -f /vagrant/deploy/systemd/fs-meter.service ]]; then
  cp /vagrant/deploy/systemd/fs-meter.service /etc/systemd/system/fs-meter.service
fi

if [[ -f /vagrant/deploy/systemd/fs-meter-restart.service ]]; then
  cp /vagrant/deploy/systemd/fs-meter-restart.service /etc/systemd/system/fs-meter-restart.service
fi

if [[ -f /vagrant/deploy/systemd/fs-meter-restart.timer ]]; then
  cp /vagrant/deploy/systemd/fs-meter-restart.timer /etc/systemd/system/fs-meter-restart.timer
fi

systemctl daemon-reload
systemctl enable fs-meter.service
systemctl enable --now fs-meter-restart.timer
systemctl start fs-meter.service || true
