#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 Clash 外部控制配置
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 检查 Clash 外部控制配置 ===")
    
    # 检查 external-controller
    print("\n1. 检查 external-controller...")
    stdin, stdout, stderr = client.exec_command("grep -E 'external-controller|secret|authentication' /etc/openclash/config.yaml 2>/dev/null || grep -E 'external-controller|secret|authentication' /etc/openclash/jiuxiang.yaml 2>/dev/null")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查 UCI 配置中的 secret
    print("\n2. 检查 dashboard_password...")
    stdin, stdout, stderr = client.exec_command("uci get openclash.config.dashboard_password 2>/dev/null")
    secret = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"Dashboard Password: {secret}")
    
    # 使用 secret 测试 API
    if secret:
        print(f"\n3. 使用 secret 测试 API...")
        stdin, stdout, stderr = client.exec_command(f"curl -s -H 'Authorization: Bearer {secret}' http://127.0.0.1:9090/proxies 2>&1 | head -50")
        print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
