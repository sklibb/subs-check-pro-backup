#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继续等待安装完成
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
    
    # 等待下载完成
    for i in range(60):
        time.sleep(5)
        
        # 检查是否还在下载
        stdin, stdout, stderr = client.exec_command("ps | grep 'wget.*openclash' | grep -v grep")
        result = stdout.read().decode('utf-8', errors='ignore')
        
        if not result.strip():
            print(f"下载完成 (等待了 {(i+1)*5} 秒)")
            break
        
        if i % 6 == 0:
            print(f"下载中... {(i+1)*5}s")
    
    # 再等待安装完成
    for i in range(12):
        time.sleep(5)
        stdin, stdout, stderr = client.exec_command("ps | grep 'opkg install' | grep -v grep")
        if not stdout.read().decode('utf-8', errors='ignore').strip():
            print(f"安装完成 (总等待 {(i+1)*5} 秒)")
            break
    
    # 检查结果
    print("\n=== 最终检查 ===")
    
    print("\n1. init.d...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '成功' || echo '失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n2. 配置目录...")
    stdin, stdout, stderr = client.exec_command("ls /etc/openclash 2>/dev/null && echo '存在' || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n3. 进程...")
    stdin, stdout, stderr = client.exec_command("ps | grep -E 'clash|openclash' | grep -v grep")
    print(stdout.read().decode('utf-8', errors='ignore') or "无进程")
    
    print("\n4. 端口...")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp | grep -E '7890|9090'")
    print(stdout.read().decode('utf-8', errors='ignore') or "端口未监听")
    
    client.close()


if __name__ == "__main__":
    main()
