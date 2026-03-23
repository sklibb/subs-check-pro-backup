#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接检查安装结果
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 检查安装结果 ===")
    
    print("\n1. init.d 脚本...")
    stdin, stdout, stderr = client.exec_command("ls -la /etc/init.d/openclash 2>/dev/null && echo '存在' || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n2. 配置目录...")
    stdin, stdout, stderr = client.exec_command("ls -la /etc/openclash 2>/dev/null && echo '存在' || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n3. 已安装包...")
    stdin, stdout, stderr = client.exec_command("opkg list-installed | grep openclash")
    print(stdout.read().decode('utf-8', errors='ignore') or "未安装")
    
    print("\n4. 进程...")
    stdin, stdout, stderr = client.exec_command("ps | grep -E 'clash|openclash' | grep -v grep")
    print(stdout.read().decode('utf-8', errors='ignore') or "无进程")
    
    print("\n5. 端口...")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp | grep -E '7890|9090'")
    print(stdout.read().decode('utf-8', errors='ignore') or "端口未监听")
    
    client.close()


if __name__ == "__main__":
    main()
