#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新下载并安装 OpenClash
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
    
    print("=== 重新下载并安装 OpenClash ===")
    
    # 清理旧文件
    print("\n1. 清理旧文件...")
    stdin, stdout, stderr = client.exec_command("rm -rf /tmp/opkg-* /var/lock/opkg.lock 2>/dev/null")
    stdout.channel.recv_exit_status()
    print("已清理")
    
    # 更新包列表
    print("\n2. 更新包列表...")
    stdin, stdout, stderr = client.exec_command("opkg update 2>&1 | tail -5")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 重新安装
    print("\n3. 重新安装...")
    stdin, stdout, stderr = client.exec_command("opkg install luci-app-openclash 2>&1")
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
    
    # 检查结果
    print("\n4. 检查结果...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '安装成功' || echo '安装失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
