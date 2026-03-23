#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查路由器网络状态
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 检查路由器网络状态 ===")
    
    # 测试 DNS
    print("\n1. 测试 DNS 解析...")
    stdin, stdout, stderr = client.exec_command("nslookup github.com 2>&1 | head -5")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 测试网络连接
    print("\n2. 测试网络连接...")
    stdin, stdout, stderr = client.exec_command("ping -c 3 8.8.8.8 2>&1")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 测试 GitHub 连接
    print("\n3. 测试 GitHub 连接...")
    stdin, stdout, stderr = client.exec_command("curl -v --connect-timeout 5 https://github.com 2>&1 | head -20")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查防火墙
    print("\n4. 检查防火墙规则...")
    stdin, stdout, stderr = client.exec_command("iptables -L OUTPUT -n 2>/dev/null | head -10")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
