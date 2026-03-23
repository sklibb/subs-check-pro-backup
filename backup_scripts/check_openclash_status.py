#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 OpenClash 安装状态
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
    
    print("=== 检查 OpenClash 安装状态 ===")
    
    # 等待安装完成
    print("\n等待安装完成...")
    time.sleep(30)
    
    # 检查 init.d
    print("\n1. 检查 init.d...")
    stdin, stdout, stderr = client.exec_command("ls -la /etc/init.d/openclash 2>/dev/null || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查配置目录
    print("\n2. 检查配置目录...")
    stdin, stdout, stderr = client.exec_command("ls -la /etc/openclash 2>/dev/null || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查进程
    print("\n3. 检查进程...")
    stdin, stdout, stderr = client.exec_command("ps | grep -E 'clash|openclash' | grep -v grep")
    print(stdout.read().decode('utf-8', errors='ignore') or "无进程")
    
    # 检查端口
    print("\n4. 检查端口...")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp | grep -E '7890|9090'")
    print(stdout.read().decode('utf-8', errors='ignore') or "端口未监听")
    
    client.close()


if __name__ == "__main__":
    main()
