#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 OpenClash 最终安装状态
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 检查 OpenClash 最终安装状态 ===")
    
    print("\n1. init.d 脚本...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null")
    result = stdout.read().decode('utf-8', errors='ignore')
    print("存在" if result.strip() else "不存在")
    
    print("\n2. 配置目录...")
    stdin, stdout, stderr = client.exec_command("ls /etc/openclash 2>/dev/null")
    result = stdout.read().decode('utf-8', errors='ignore')
    print("存在" if result.strip() else "不存在")
    
    print("\n3. 共享目录...")
    stdin, stdout, stderr = client.exec_command("ls /usr/share/openclash 2>/dev/null")
    result = stdout.read().decode('utf-8', errors='ignore')
    print("存在" if result.strip() else "不存在")
    
    print("\n4. 进程...")
    stdin, stdout, stderr = client.exec_command("ps | grep clash | grep -v grep")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(result if result.strip() else "无进程")
    
    print("\n5. 端口...")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp | grep 7890")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(result if result.strip() else "端口未监听")
    
    client.close()


if __name__ == "__main__":
    main()
