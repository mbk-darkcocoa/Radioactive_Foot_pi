#!/usr/bin/env python3
"""
eBPF VFS open monitor with in-kernel inode/device directory filtering.

The monitor preloads a BPF hash map with directory ``st_dev``/``st_ino`` pairs
before attaching a kprobe to ``vfs_open``. The kernel program drops events for
opens whose immediate parent directory is not in that map, avoiding avoidable
perf-buffer traffic and user-space processing.
"""

from __future__ import annotations

import argparse
import ctypes as ct
import json
import logging
import os
import signal
import sys
import time
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

try:
    from bcc import BPF
except ImportError:  # pragma: no cover - dependency checked at runtime
    BPF = None  # type: ignore[assignment]

try:
    from prometheus_client import Counter, Gauge, start_http_server
except ImportError:  # pragma: no cover - dependency checked at runtime
    Counter = Gauge = None  # type: ignore[assignment]
    start_http_server = None  # type: ignore[assignment]

try:
    from kafka import KafkaProducer
except ImportError:  # pragma: no cover - dependency checked at runtime
    KafkaProducer = None  # type: ignore[assignment]


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
LOGGER = logging.getLogger("fs_meter_kernel_filtered")

DEFAULT_WATCH_DIRECTORIES = [
    "/etc",
    "/var/log",
    "/mnt/off_device",
    "/tmp/billing_test",
]

BPF_PROGRAM = r"""
#include <uapi/linux/ptrace.h>
#include <linux/dcache.h>
#include <linux/fs.h>
#include <linux/limits.h>
#include <linux/mnt_namespace.h>
#include <linux/nsproxy.h>
#include <linux/path.h>
#include <linux/sched.h>

struct watch_key_t {
    u64 dev;
    u64 ino;
};

#define FILE_NAME_LEN 256

struct event_t {
    u32 pid;
    u32 tgid;
    u64 dir_dev;
    u64 dir_ino;
    u64 file_ino;
    u64 mnt_ns_inum;
    u64 root_mnt_ns_inum;
    u32 billing_milliunits;
    char comm[TASK_COMM_LEN];
    char filename[FILE_NAME_LEN];
};

BPF_HASH(watched_dirs, struct watch_key_t, u8, 4096);
BPF_ARRAY(root_mount_ns, u64, 1);
BPF_PERF_OUTPUT(events);

int trace_vfs_open(struct pt_regs *ctx, struct path *path, struct file *file)
{
    struct dentry *dentry = NULL;
    struct dentry *parent = NULL;
    struct inode *dir_inode = NULL;
    struct inode *inode = NULL;
    struct super_block *sb = NULL;
    struct task_struct *task = NULL;
    struct nsproxy *nsproxy = NULL;
    struct mnt_namespace *mnt_ns = NULL;
    struct watch_key_t key = {};
    u8 *enabled;
    u32 idx = 0;
    u64 *root_mnt_ns;
    struct event_t event = {};
    u64 pid_tgid = bpf_get_current_pid_tgid();

    if (!file) {
        return 0;
    }

    bpf_probe_read_kernel(&dentry, sizeof(dentry), &file->f_path.dentry);
    if (!dentry) {
        return 0;
    }

    bpf_probe_read_kernel(&parent, sizeof(parent), &dentry->d_parent);
    if (!parent) {
        return 0;
    }

    bpf_probe_read_kernel(&dir_inode, sizeof(dir_inode), &parent->d_inode);
    bpf_probe_read_kernel(&inode, sizeof(inode), &dentry->d_inode);
    if (!dir_inode || !inode) {
        return 0;
    }

    bpf_probe_read_kernel(&sb, sizeof(sb), &dir_inode->i_sb);
    if (!sb) {
        return 0;
    }

    bpf_probe_read_kernel(&key.dev, sizeof(key.dev), &sb->s_dev);
    bpf_probe_read_kernel(&key.ino, sizeof(key.ino), &dir_inode->i_ino);
    enabled = watched_dirs.lookup(&key);
    if (!enabled) {
        return 0;
    }

    event.pid = pid_tgid;
    event.tgid = pid_tgid >> 32;
    event.dir_dev = key.dev;
    event.dir_ino = key.ino;
    bpf_probe_read_kernel(&event.file_ino, sizeof(event.file_ino), &inode->i_ino);
    task = (struct task_struct *)bpf_get_current_task();
    if (task) {
        bpf_probe_read_kernel(&nsproxy, sizeof(nsproxy), &task->nsproxy);
    }
    if (nsproxy) {
        bpf_probe_read_kernel(&mnt_ns, sizeof(mnt_ns), &nsproxy->mnt_ns);
    }
    if (mnt_ns) {
        bpf_probe_read_kernel(&event.mnt_ns_inum, sizeof(event.mnt_ns_inum), &mnt_ns->ns.inum);
    }
    root_mnt_ns = root_mount_ns.lookup(&idx);
    if (root_mnt_ns) {
        event.root_mnt_ns_inum = *root_mnt_ns;
    }
    if (event.root_mnt_ns_inum &&
        event.mnt_ns_inum &&
        event.mnt_ns_inum != event.root_mnt_ns_inum) {
        event.billing_milliunits = 175;
    }
    bpf_get_current_comm(&event.comm, sizeof(event.comm));
    bpf_probe_read_kernel_str(&event.filename, sizeof(event.filename), dentry->d_name.name);
    events.perf_submit(ctx, &event, sizeof(event));

    return 0;
}
"""


class WatchKey(ct.Structure):
    _fields_ = [
        ("dev", ct.c_ulonglong),
        ("ino", ct.c_ulonglong),
    ]


class Event(ct.Structure):
    _fields_ = [
        ("pid", ct.c_uint),
        ("tgid", ct.c_uint),
        ("dir_dev", ct.c_ulonglong),
        ("dir_ino", ct.c_ulonglong),
        ("file_ino", ct.c_ulonglong),
        ("mnt_ns_inum", ct.c_ulonglong),
        ("root_mnt_ns_inum", ct.c_ulonglong),
        ("billing_milliunits", ct.c_uint),
        ("comm", ct.c_char * 16),
        ("filename", ct.c_char * 256),
    ]


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directories",
        nargs="*",
        default=DEFAULT_WATCH_DIRECTORIES,
        help="Directories to watch recursively.",
    )
    parser.add_argument(
        "--metrics-port",
        type=int,
        default=0,
        help="Prometheus metrics port. Disabled when 0.",
    )
    parser.add_argument(
        "--kafka-bootstrap-servers",
        default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", ""),
        help="Optional Kafka bootstrap server list.",
    )
    parser.add_argument(
        "--kafka-topic",
        default=os.getenv("KAFKA_TOPIC", "fs-meter-events"),
        help="Kafka topic for emitted events.",
    )
    parser.add_argument(
        "--poll-timeout-ms",
        type=int,
        default=1000,
        help="perf buffer poll timeout in milliseconds.",
    )
    parser.add_argument(
        "--root-mnt-ns-inum",
        type=int,
        default=0,
        help="Root mount namespace inode for sandbox billing checks. Auto-detected from /proc/1/ns/mnt when unset.",
    )
    return parser.parse_args(argv)


def normalize_watch_directories(directories: Sequence[str]) -> List[str]:
    normalized: List[str] = []
    seen = set()
    for directory in directories:
        candidate = os.path.realpath(directory)
        if candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)
    return normalized


def iter_directory_stats(directories: Sequence[str]) -> Iterator[Tuple[str, os.stat_result]]:
    seen_pairs = set()
    for root in normalize_watch_directories(directories):
        if not os.path.isdir(root):
            LOGGER.warning("Skipping non-directory watch target: %s", root)
            continue

        for current_root, dirnames, _, in os.walk(root, followlinks=False):
            try:
                stat_result = os.stat(current_root, follow_symlinks=False)
            except OSError as exc:
                LOGGER.warning("Unable to stat directory %s: %s", current_root, exc)
                continue

            key = (stat_result.st_dev, stat_result.st_ino)
            if key in seen_pairs:
                dirnames[:] = []
                continue

            seen_pairs.add(key)
            yield current_root, stat_result


def load_watch_directories(watch_table, directories: Sequence[str]) -> Dict[Tuple[int, int], str]:
    loaded: Dict[Tuple[int, int], str] = {}

    for directory, stat_result in iter_directory_stats(directories):
        key = WatchKey(dev=stat_result.st_dev, ino=stat_result.st_ino)
        watch_table[key] = ct.c_ubyte(1)
        loaded[(stat_result.st_dev, stat_result.st_ino)] = directory

    if not loaded:
        raise RuntimeError("No valid watch directories were loaded into the BPF map.")

    LOGGER.info("Loaded %d directory inode/device pairs into watched_dirs", len(loaded))
    return loaded


def resolve_root_mount_namespace_inode(cli_value: int) -> int:
    if cli_value > 0:
        return cli_value
    return int(os.stat("/proc/1/ns/mnt", follow_symlinks=False).st_ino)


def load_root_mount_namespace(root_mount_ns_table, namespace_inode: int) -> None:
    root_mount_ns_table[ct.c_int(0)] = ct.c_ulonglong(namespace_inode)
    LOGGER.info("Configured root mount namespace inode: %d", namespace_inode)


def start_metrics(metrics_port: int):
    if metrics_port <= 0:
        return None, None, None
    if not all((Counter, Gauge, start_http_server)):
        raise RuntimeError("prometheus_client is required when --metrics-port is enabled.")

    start_http_server(metrics_port)
    opens_counter = Counter(
        "fs_meter_open_events_total",
        "File open events forwarded from the perf buffer.",
    )
    watched_gauge = Gauge(
        "fs_meter_watched_directories",
        "Directory inode/device pairs loaded into the BPF watch map.",
    )
    billing_counter = Counter(
        "fs_meter_off_device_billing_milliunits_total",
        "Total milliunits billed for mount namespace mismatches.",
    )
    LOGGER.info("Prometheus metrics exposed on port %d", metrics_port)
    return opens_counter, watched_gauge, billing_counter


def build_kafka_producer(bootstrap_servers: str):
    if not bootstrap_servers:
        return None
    if KafkaProducer is None:
        raise RuntimeError("kafka-python is required when Kafka output is enabled.")

    producer = KafkaProducer(
        bootstrap_servers=[server.strip() for server in bootstrap_servers.split(",") if server.strip()],
        value_serializer=lambda payload: json.dumps(payload, sort_keys=True).encode("utf-8"),
    )
    LOGGER.info("Kafka producer enabled for %s", bootstrap_servers)
    return producer


def decode_c_string(raw_value: bytes) -> str:
    return raw_value.split(b"\x00", 1)[0].decode("utf-8", errors="replace")


def build_event_payload(cpu: int, data, size: int, loaded_directories: Dict[Tuple[int, int], str]) -> Dict[str, object]:
    event = ct.cast(data, ct.POINTER(Event)).contents
    directory_key = (int(event.dir_dev), int(event.dir_ino))
    billing_milliunits = int(event.billing_milliunits)
    return {
        "timestamp": time.time(),
        "cpu": cpu,
        "size": size,
        "pid": int(event.pid),
        "tgid": int(event.tgid),
        "comm": decode_c_string(bytes(event.comm)),
        "filename": decode_c_string(bytes(event.filename)),
        "file_inode": int(event.file_ino),
        "directory_device": int(event.dir_dev),
        "directory_inode": int(event.dir_ino),
        "mount_namespace_inode": int(event.mnt_ns_inum),
        "root_mount_namespace_inode": int(event.root_mnt_ns_inum),
        "off_device_access": bool(billing_milliunits),
        "billing_milliunits": billing_milliunits,
        "billing_units": billing_milliunits / 100.0,
        "watched_directory": loaded_directories.get(directory_key, ""),
        "kprobe": "vfs_open",
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    if BPF is None:
        LOGGER.error("bcc is required to run this script.")
        return 1

    opens_counter, watched_gauge, billing_counter = start_metrics(args.metrics_port)
    producer = build_kafka_producer(args.kafka_bootstrap_servers)
    root_mount_namespace_inode = resolve_root_mount_namespace_inode(args.root_mnt_ns_inum)

    bpf = BPF(text=BPF_PROGRAM)
    loaded_directories = load_watch_directories(bpf["watched_dirs"], args.directories)
    load_root_mount_namespace(bpf["root_mount_ns"], root_mount_namespace_inode)

    if watched_gauge is not None:
        watched_gauge.set(len(loaded_directories))

    bpf.attach_kprobe(event="vfs_open", fn_name="trace_vfs_open")
    LOGGER.info("Attached kprobe to vfs_open")

    stop_requested = False

    def handle_stop(signum, _frame):
        nonlocal stop_requested
        stop_requested = True
        LOGGER.info("Received signal %s, shutting down", signum)

    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)

    def on_event(cpu, data, size):
        payload = build_event_payload(cpu, data, size, loaded_directories)
        print(json.dumps(payload, sort_keys=True), flush=True)
        if opens_counter is not None:
            opens_counter.inc()
        if billing_counter is not None and payload["billing_milliunits"]:
            billing_counter.inc(payload["billing_milliunits"])
        if producer is not None:
            producer.send(args.kafka_topic, payload)

    bpf["events"].open_perf_buffer(on_event)
    LOGGER.info("Monitoring directories: %s", ", ".join(sorted(loaded_directories.values())))

    try:
        while not stop_requested:
            bpf.perf_buffer_poll(timeout=args.poll_timeout_ms)
    finally:
        if producer is not None:
            producer.flush(timeout=5)
            producer.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
