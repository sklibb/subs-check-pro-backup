#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查安装失败原因
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 检查安装失败原因 ===")
    
    # 检查已安装的包
    print("\n1. 已安装的包...")
    stdin, stdout, stderr = client.exec_command("opkg list-installed | grep openclash")
    print(stdout.read().decode('utf-8', errors='ignore') or "无")
    
    # 检查下载的包
    print("\n2. 下载的包...")
    stdin, stdout, stderr = client.exec_command("ls -la /tmp/opkg-*/luci-app-openclash* 2>/dev/null")
    print(stdout.read().decode('utf-8', errors='ignore') or "无")
    
    # 手动安装
    print("\n3. 手动安装...")
    stdin, stdout, stderr = client.exec_command("cd /tmp && opkg install --force-reinstall /tmp/opkg-*/luci-app-openclash*.ipk 2>&1")
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    print(output)
    if error:
        print(f"错误: {error}")
    
    # 检查结果
    print("\n4. 检查结果...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '成功' || echo '失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
