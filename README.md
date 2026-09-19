# Radioactive_Foot_pi
A RF/radioactive foot pi implementation and virtual server framework with lightning speed blazing fast 6GLTJ.

## Run as a VM (Vagrant + systemd)

### 1) Start the VM

```bash
# Ubuntu (default)
vagrant up

# Fedora
VM_OS=fedora vagrant up
```

Enable direct bridged/public networking ("real internet"):

```bash
REAL_INTERNET=1 vagrant up
# Optional explicit bridge selection
REAL_INTERNET=1 BRIDGE_INTERFACE="en0: Wi-Fi (Wireless)" vagrant up
```

The VM bootstrap script installs Python + BCC tooling, syncs the repository into `/opt/radioactive-foot-pi`, and installs systemd units from:

- `/opt/radioactive-foot-pi/deploy/systemd/fs-meter.service`

### 2) Check monitor status

```bash
vagrant ssh -c "sudo systemctl status fs-meter.service --no-pager"
```

### 3) Follow logs

```bash
vagrant ssh -c "sudo journalctl -u fs-meter.service -f"
```

## fs_meter settings behavior

- Runtime settings file: `common/fs_meter_settings.json`
- CLI positional directories are **merged** with `watch_directories` from the settings file.
- `root_mnt_ns_inum` overrides namespace auto-detection when set.
- `root_mnt_ns_source` controls auto-detection source: `self`, `pid1`, or `pid`.
- `root_mnt_ns_pid` is required when `root_mnt_ns_source` is `pid`.
- Default `root_mnt_ns_source` is `pid1`.
