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
    
    # 等待安装完成
    for i in range(30):
        time.sleep(5)
        stdin, stdout, stderr = client.exec_command("ps | grep 'opkg install' | grep -v grep")
        if not stdout.read().decode('utf-8', errors='ignore').strip():
            print(f"安装进程已结束 (等待了 {(i+1)*5} 秒)")
            break
        if i % 3 == 0:
            print(f"等待中... {(i+1)*5}s")
    
    # 检查结果
    print("\n=== 检查结果 ===")
    
    print("\n1. 检查 init.d...")
    stdin, stdout, stderr = client.exec_command("ls -la /etc/init.d/openclash 2>/dev/null && echo '安装成功' || echo '安装失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n2. 检查配置目录...")
    stdin, stdout, stderr = client.exec_command("ls /etc/openclash 2>/dev/null && echo '存在' || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n3. 检查进程...")
    stdin, stdout, stderr = client.exec_command("ps | grep -E 'clash|openclash' | grep -v grep")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(result if result.strip() else "无进程")
    
    print("\n4. 检查端口...")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp | grep -E '7890|9090'")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(result if result.strip() else "端口未监听")
    
    client.close()


if __name__ == "__main__":
    main()
