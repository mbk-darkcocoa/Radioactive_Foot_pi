#!/usr/bin/env bash
set -euo pipefail

install_dependencies() {
  local distro_id="$1"
  case "$distro_id" in
    ubuntu)
      export DEBIAN_FRONTEND=noninteractive
      apt-get update
      apt-get install -y \
        python3 \
        python3-pip \
        python3-bpfcc \
        bpfcc-tools \
        rsync
      apt-get install -y "linux-headers-$(uname -r)" || apt-get install -y linux-headers-generic
      ;;
    debian)
      export DEBIAN_FRONTEND=noninteractive
      apt-get update
      apt-get install -y \
        python3 \
        python3-pip \
        python3-bpfcc \
        bpfcc-tools \
        rsync
      apt-get install -y "linux-headers-$(uname -r)" || apt-get install -y linux-headers-amd64
      ;;
    fedora)
      dnf install -y \
        python3 \
        python3-pip \
        python3-bcc \
        bcc-tools \
        kernel-devel \
        rsync
      ;;
    *)
      echo "Unsupported Linux distribution: ${distro_id}" >&2
      exit 1
      ;;
  esac
}

if [[ ! -f /etc/os-release ]]; then
  echo "Cannot detect operating system: /etc/os-release missing." >&2
  exit 1
fi

# shellcheck disable=SC1091
source /etc/os-release
install_dependencies "${ID}"

install -d -m 0755 /opt/radioactive-foot-pi
rsync -a --delete --exclude ".git" /vagrant/ /opt/radioactive-foot-pi/

if [[ ! -f /opt/radioactive-foot-pi/deploy/systemd/fs-meter.service ]]; then
  echo "Missing required unit file: /opt/radioactive-foot-pi/deploy/systemd/fs-meter.service" >&2
  exit 1
fi

install -m 0644 -T /opt/radioactive-foot-pi/deploy/systemd/fs-meter.service /etc/systemd/system/fs-meter.service

install -d -m 0755 /etc/default /etc/sysconfig
cat >/etc/default/fs-meter <<'EOF'
APP_ROOT=/opt/radioactive-foot-pi
SETTINGS_FILE=/opt/radioactive-foot-pi/common/fs_meter_settings.json
EOF
cat >/etc/sysconfig/fs-meter <<'EOF'
APP_ROOT=/opt/radioactive-foot-pi
SETTINGS_FILE=/opt/radioactive-foot-pi/common/fs_meter_settings.json
EOF

systemctl daemon-reload
systemctl enable fs-meter.service
systemctl start fs-meter.service
