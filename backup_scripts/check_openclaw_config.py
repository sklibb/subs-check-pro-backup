#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 OpenClaw 代理端口
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== OpenClaw 配置 ===")
    stdin, stdout, stderr = client.exec_command("cat /etc/openclash/config.yaml 2>/dev/null | head -50")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 查找代理端口 ===")
    stdin, stdout, stderr = client.exec_command("grep -E 'port:|socks-port:|mixed-port:|redir-port:' /etc/openclash/config.yaml 2>/dev/null")
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output if output.strip() else "未找到端口配置")
    
    print("\n=== OpenClaw UCI 配置 ===")
    stdin, stdout, stderr = client.exec_command("cat /etc/config/openclash | grep -E 'proxy_port|http_port|socks_port|mixed_port' | head -10")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
