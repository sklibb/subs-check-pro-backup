#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继续等待 OpenClash 安装
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
    
    print("=== 继续等待 OpenClash 安装 ===")
    
    # 等待安装完成
    for i in range(20):
        print(f"\n等待中... ({i+1}/20)")
        time.sleep(10)
        
        # 检查是否还在安装
        stdin, stdout, stderr = client.exec_command("ps | grep 'opkg install' | grep -v grep")
        result = stdout.read().decode('utf-8', errors='ignore')
        if not result.strip():
            print("安装进程已结束")
            break
        else:
            print(f"仍在安装: {result.strip()[:50]}...")
    
    # 检查结果
    print("\n=== 最终检查 ===")
    
    print("\n1. 检查 init.d...")
    stdin, stdout, stderr = client.exec_command("ls -la /etc/init.d/openclash 2>/dev/null || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n2. 检查配置目录...")
    stdin, stdout, stderr = client.exec_command("ls -la /etc/openclash 2>/dev/null || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n3. 检查进程...")
    stdin, stdout, stderr = client.exec_command("ps | grep -E 'clash|openclash' | grep -v grep")
    print(stdout.read().decode('utf-8', errors='ignore') or "无进程")
    
    print("\n4. 检查端口...")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp | grep -E '7890|9090'")
    print(stdout.read().decode('utf-8', errors='ignore') or "端口未监听")
    
    client.close()


if __name__ == "__main__":
    main()
