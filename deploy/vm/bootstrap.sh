#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y \
  python3 \
  python3-pip \
  python3-bpfcc \
  bpfcc-tools \
  linux-headers-generic \
  rsync

install -d -m 0755 /opt/radioactive-foot-pi
rsync -a --delete --exclude ".git" /vagrant/ /opt/radioactive-foot-pi/

if [[ ! -f /opt/radioactive-foot-pi/deploy/systemd/fs-meter.service ]]; then
  echo "Missing required unit file: /opt/radioactive-foot-pi/deploy/systemd/fs-meter.service" >&2
  exit 1
fi

cp /opt/radioactive-foot-pi/deploy/systemd/fs-meter.service /etc/systemd/system/fs-meter.service

if [[ -f /opt/radioactive-foot-pi/deploy/systemd/fs-meter-restart.service ]]; then
  cp /opt/radioactive-foot-pi/deploy/systemd/fs-meter-restart.service /etc/systemd/system/fs-meter-restart.service
fi

if [[ -f /opt/radioactive-foot-pi/deploy/systemd/fs-meter-restart.timer ]]; then
  cp /opt/radioactive-foot-pi/deploy/systemd/fs-meter-restart.timer /etc/systemd/system/fs-meter-restart.timer
fi

cat >/etc/default/fs-meter <<'EOF'
APP_ROOT=/opt/radioactive-foot-pi
SETTINGS_FILE=/opt/radioactive-foot-pi/common/fs_meter_settings.json
EOF

systemctl daemon-reload
systemctl enable fs-meter.service
if [[ -f /etc/systemd/system/fs-meter-restart.timer ]]; then
  systemctl enable --now fs-meter-restart.timer
fi
systemctl start fs-meter.service
