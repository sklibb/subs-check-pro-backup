#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 OpenClaw 代理节点状态
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"
PROXY_USER = "Clash"
PROXY_PASS = "vLzYmzrv"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 检查 Clash 代理状态 ===")
    
    # 检查代理选择
    print("\n1. 检查当前代理选择...")
    cmd = f"curl -s -u {PROXY_USER}:{PROXY_PASS} http://127.0.0.1:9090/proxies 2>&1 | head -100"
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查节点延迟
    print("\n2. 检查节点延迟...")
    stdin, stdout, stderr = client.exec_command("cat /etc/openclash/config/jiuxiang.yaml | grep -A 20 'proxy-groups:' | head -25")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 测试节点连接
    print("\n3. 测试节点服务器连接...")
    stdin, stdout, stderr = client.exec_command("nc -zv -w 3 f4d7f1c2f3b80976a5e2c1d4b3f0f321.358.onl 55011 2>&1")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
