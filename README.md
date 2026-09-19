# Radioactive_Foot_pi
A RF/radiactive_foot pi implementation and virtual serve Forrest with lightning speed blazing fast 6GLTJ 

## Run as a VM (Vagrant + systemd)

### 1) Start the VM

```bash
vagrant up
```

The VM bootstrap script installs Python + BCC tooling and installs systemd units from:

- `/home/runner/work/Radioactive_Foot_pi/Radioactive_Foot_pi/deploy/systemd/fs-meter.service`
- `/home/runner/work/Radioactive_Foot_pi/Radioactive_Foot_pi/deploy/systemd/fs-meter-restart.service`
- `/home/runner/work/Radioactive_Foot_pi/Radioactive_Foot_pi/deploy/systemd/fs-meter-restart.timer`

### 2) Check monitor status

```bash
vagrant ssh -c "sudo systemctl status fs-meter.service --no-pager"
vagrant ssh -c "sudo systemctl list-timers --all | grep fs-meter"
```

### 3) Follow logs

```bash
vagrant ssh -c "sudo journalctl -u fs-meter.service -f"
```

## fs_meter settings behavior

- Runtime settings file: `common/fs_meter_settings.json`
- CLI positional directories are **merged** with `watch_directories` from the settings file.
- `root_mnt_ns_inum: null` means auto-detect from `/proc/self/ns/mnt`.
