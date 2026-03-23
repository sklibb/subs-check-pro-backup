#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 OpenClaw 详细状态
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== OpenClaw 日志 ===")
    stdin, stdout, stderr = client.exec_command("logread | grep -i clash | tail -30")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== Clash 进程 ===")
    stdin, stdout, stderr = client.exec_command("ps | grep clash | grep -v grep")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 测试直连 ===")
    stdin, stdout, stderr = client.exec_command("curl -s --connect-timeout 5 http://www.baidu.com 2>&1 | head -3")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 检查 Clash 配置 ===")
    stdin, stdout, stderr = client.exec_command("cat /etc/openclash/config.yaml 2>/dev/null | head -30")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
