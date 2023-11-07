#!/usr/bin/env python3
import argparse
import errno
import os
import re
import subprocess
import sys
import time
import traceback

argparser = argparse.ArgumentParser()
argparser.add_argument('prepost', choices=['pre', 'post'])
argparser.add_argument('event')

LAST_DEVICE_FILE = '/tmp/last-bluetooth-device'
CONNECT_RETRY_SECS = 10

def get_connected_device_mac_addresses():
    ret = []
    try:
        output = subprocess.check_output([
            'bluetoothctl',
            'info',
        ]).decode()
    except subprocess.CalledProcessError:
        # happens when e.g. Bluetooth is disabled
        return ret

    for line in output.splitlines():
        if not line.startswith('Device '):
            continue
        ret.append(line.split()[1])

    return ret


def main(args):
    if args.event != 'suspend':
        return

    if args.prepost == 'pre':
        devices = get_connected_device_mac_addresses()

        try:
            os.remove(LAST_DEVICE_FILE)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

        if len(devices) == 1:
            with open(LAST_DEVICE_FILE, 'w') as f:
                f.write(devices[0] + '\n')

    elif args.prepost == 'post':
        try:
            with open(LAST_DEVICE_FILE) as f:
                device = f.read().strip()
        except FileNotFoundError:
            return

        if not re.fullmatch(r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}', device):
            raise ValueError(f'invalid device MAC address {device}')

        start_time = time.time()
        while time.time() < start_time + CONNECT_RETRY_SECS:
            try:
                subprocess.check_call([
                    'bluetoothctl',
                    'connect',
                    device,
                ])
            except:
                time.sleep(0.1)

    else:
        raise RuntimeError('unreachable')


if __name__ == '__main__' and not hasattr(sys, 'ps1'):
    try:
        main(argparser.parse_args())
    except:
        with open('/tmp/exception', 'w') as f:
            traceback.print_exc(file=f)
        raise
