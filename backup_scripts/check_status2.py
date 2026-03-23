#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持续检查检测状态
"""

import paramiko
import time

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 等待检测进行 ===")
    time.sleep(30)
    
    print("\n=== 最新日志 ===")
    stdin, stdout, stderr = client.exec_command("docker logs subs-check-pro --tail 50 2>&1")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
