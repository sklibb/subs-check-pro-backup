#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查路由器代理端口
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 所有监听端口 ===")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp 2>/dev/null || ss -tlnp")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 检查 OpenClaw 配置 ===")
    stdin, stdout, stderr = client.exec_command("find /etc /opt /tmp -name '*openclaw*' -o -name '*clash*' 2>/dev/null | head -20")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 检查常见代理配置 ===")
    stdin, stdout, stderr = client.exec_command("cat /etc/openclash/config.yaml 2>/dev/null | head -30 || cat /opt/openclash/config.yaml 2>/dev/null | head -30")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
