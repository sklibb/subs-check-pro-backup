#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等待安装完成
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
    
    print("=== 等待安装完成 ===")
    
    # 等待
    for i in range(60):
        time.sleep(5)
        
        # 检查是否还在安装
        stdin, stdout, stderr = client.exec_command("ps | grep 'opkg install' | grep -v grep")
        if not stdout.read().decode('utf-8', errors='ignore').strip():
            print(f"安装进程已结束 (等待了 {(i+1)*5} 秒)")
            break
        
        if i % 12 == 0:
            print(f"等待中... {(i+1)*5}s")
    
    # 检查结果
    print("\n=== 检查结果 ===")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '成功' || echo '失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    stdin, stdout, stderr = client.exec_command("ls /usr/share/openclash 2>/dev/null && echo '存在' || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
