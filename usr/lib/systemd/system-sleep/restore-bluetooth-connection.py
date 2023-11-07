#!/usr/bin/env python3
import argparse
import errno
import os
import re
import subprocess
import sys

argparser = argparse.ArgumentParser()
argparser.add_argument(
    'transition', help='either "pre" or "post"',
    choices=['pre', 'post'])

LAST_DEVICE_FILE = '/tmp/last-bluetooth-device'

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
    if args.transition == 'pre':
        devices = get_connected_device_mac_addresses()

        try:
            os.remove(LAST_DEVICE_FILE)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

        if len(devices) == 1:
            with open(LAST_DEVICE_FILE, 'w') as f:
                f.write(devices[0] + '\n')

    elif args.transition == 'post':
        try:
            with open(LAST_DEVICE_FILE) as f:
                device = f.read().strip()
        except FileNotFoundError:
            return

        if not re.fullmatch(r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}', device):
            raise ValueError(f'invalid device MAC address {device}')

        subprocess.check_call([
            'bluetoothctl',
            'connect',
            device,
        ])
    else:
        raise RuntimeError('unreachable')


if __name__ == '__main__' and not hasattr(sys, 'ps1'):
    main(argparser.parse_args())
