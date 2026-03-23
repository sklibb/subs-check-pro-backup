#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 Clash 实际配置
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== Clash 配置文件路径 ===")
    stdin, stdout, stderr = client.exec_command("ls -la /etc/openclash/*.yaml 2>/dev/null")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 实际使用的配置 ===")
    stdin, stdout, stderr = client.exec_command("cat /etc/openclash/config/jiuxiang.yaml 2>/dev/null | head -50")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 检查代理组 ===")
    stdin, stdout, stderr = client.exec_command("grep -A 5 'proxy-groups:' /etc/openclash/config/jiuxiang.yaml 2>/dev/null | head -20")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 检查节点 ===")
    stdin, stdout, stderr = client.exec_command("grep -A 3 'proxies:' /etc/openclash/config/jiuxiang.yaml 2>/dev/null | head -10")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
