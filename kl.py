#!/usr/bin/python3

import os
import re

GREEN = "\033[1;32;40m"
RESET = "\033[0m"

def parse_ssh_config():
    ssh_config_path = os.path.expanduser('~/.ssh/config')

    if not os.path.exists(ssh_config_path):
        print("SSH config file not found!")
        return

    hosts_map = {}  # {host: (hostname, aliases)}
    current_hostname = None

    with open(ssh_config_path, 'r') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            parts = line.lower().split()
            if len(parts) < 2:
                continue

            key, value = parts[0], parts[1]

            if key.lower() == 'host':
                hosts = line.split(None, 1)[1].split()
                main_host = hosts[0]
                aliases = hosts[1:] if len(hosts) > 1 else []
                if main_host != '*':
                    hosts_map[main_host] = (None, aliases)

            elif key.lower() == 'hostname':
                hostname = value
                for host, (_, aliases) in hosts_map.items():
                    if hosts_map[host][0] is None:
                        hosts_map[host] = (hostname, aliases)

    for host, (hostname, aliases) in hosts_map.items():
        if hostname and not host.startswith('#'):
            alias_str = f" ( {' '.join(aliases)} )" if aliases else ""
            print(f"# ssh {GREEN}{host}{RESET} ---> {GREEN}{hostname}{RESET}{alias_str}")

if __name__ == "__main__":
    parse_ssh_config()
