#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继续等待
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
    
    print("=== 继续等待 ===")
    
    # 等待下载完成
    for i in range(60):
        time.sleep(5)
        
        stdin, stdout, stderr = client.exec_command("ps | grep 'wget.*openclash' | grep -v grep")
        result = stdout.read().decode('utf-8', errors='ignore')
        
        if not result.strip():
            print(f"下载完成 (总等待 {(i+1)*5} 秒)")
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
    print("\n=== 检查 ===")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '成功' || echo '失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    stdin, stdout, stderr = client.exec_command("ls /etc/openclash 2>/dev/null && echo '存在' || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
