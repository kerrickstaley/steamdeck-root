#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys

argparser = argparse.ArgumentParser()
argparser.add_argument(
    'transition', help='either "pre" or "post"',
    choices=['pre', 'post'])


def get_connected_device_mac_addresses():
    ret = []
    output = subprocess.check_output([
        'bluetoothctl',
        'devices',
        'Connected',
    ]).decode()

    for line in output.splitlines():
        ret.append(line.split()[1])

    return ret

def main(args):
    if args.transition == 'pre':
        devices = get_connected_device_mac_addresses()
        with open('/tmp/last-bluetooth-device', 'w') as f:
            if len(devices) == 1:
                f.write(devices[0] + '\n')
    elif args.transition == 'post':
        try:
            with open('/tmp/last-bluetooth-device') as f:
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
