#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查可用的包源
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 检查包源 ===")
    
    # 检查配置文件
    print("\n1. 包源配置...")
    stdin, stdout, stderr = client.exec_command("cat /etc/opkg/distfeeds.conf 2>/dev/null")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 搜索 openclash
    print("\n2. 搜索 openclash...")
    stdin, stdout, stderr = client.exec_command("opkg list | grep -i openclash | head -10")
    print(stdout.read().decode('utf-8', errors='ignore') or '无结果')
    
    # 搜索 clash
    print("\n3. 搜索 clash...")
    stdin, stdout, stderr = client.exec_command("opkg list | grep -i clash | head -20")
    print(stdout.read().decode('utf-8', errors='ignore') or '无结果')
    
    client.close()


if __name__ == "__main__":
    main()
