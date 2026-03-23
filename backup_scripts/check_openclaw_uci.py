#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 OpenClaw 网关配置
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== OpenClaw UCI 完整配置 ===")
    stdin, stdout, stderr = client.exec_command("cat /etc/config/openclash")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 检查透明代理模式 ===")
    stdin, stdout, stderr = client.exec_command("uci get openclash.config.proxy_mode 2>/dev/null")
    print(f"代理模式: {stdout.read().decode('utf-8', errors='ignore').strip() or '未设置'}")
    
    print("\n=== 检查是否启用代理端口 ===")
    stdin, stdout, stderr = client.exec_command("uci get openclash.config.enable_proxy 2>/dev/null")
    print(f"启用代理端口: {stdout.read().decode('utf-8', errors='ignore').strip() or '未设置'}")
    
    client.close()


if __name__ == "__main__":
    main()
