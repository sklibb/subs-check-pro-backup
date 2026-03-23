#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等待 OpenClash 安装完成
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
    
    print("=== 等待 OpenClash 安装完成 ===")
    
    # 等待下载完成
    for i in range(60):
        time.sleep(5)
        
        stdin, stdout, stderr = client.exec_command("ps | grep 'wget.*openclash' | grep -v grep")
        if not stdout.read().decode('utf-8', errors='ignore').strip():
            print(f"下载完成 (等待了 {(i+1)*5} 秒)")
            break
        
        if i % 12 == 0:
            print(f"下载中... {(i+1)*5}s")
    
    # 等待安装完成
    for i in range(24):
        time.sleep(5)
        stdin, stdout, stderr = client.exec_command("ps | grep 'opkg install' | grep -v grep")
        if not stdout.read().decode('utf-8', errors='ignore').strip():
            print(f"安装完成")
            break
    
    # 检查结果
    print("\n=== 最终检查 ===")
    
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null")
    print(f"init.d: {'存在' if stdout.read().decode('utf-8', errors='ignore').strip() else '不存在'}")
    
    stdin, stdout, stderr = client.exec_command("ls /etc/openclash 2>/dev/null")
    print(f"配置目录：{'存在' if stdout.read().decode('utf-8', errors='ignore').strip() else '不存在'}")
    
    stdin, stdout, stderr = client.exec_command("ls /usr/share/openclash 2>/dev/null")
    print(f"共享目录：{'存在' if stdout.read().decode('utf-8', errors='ignore').strip() else '不存在'}")
    
    client.close()


if __name__ == "__main__":
    main()
