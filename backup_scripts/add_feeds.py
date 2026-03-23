#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 OpenClash 源并安装
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 添加 OpenClash 源并安装 ===")
    
    # 添加 OpenClash 源
    print("\n1. 添加 OpenClash 源...")
    stdin, stdout, stderr = client.exec_command("echo 'src/gz openclash https://raw.githubusercontent.com/senshine/openwrt_openclash/master' >> /etc/opkg/distfeeds.conf")
    stdout.channel.recv_exit_status()
    
    # 更新包列表
    print("\n2. 更新包列表...")
    stdin, stdout, stderr = client.exec_command("opkg update 2>&1 | tail -5")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 搜索
    print("\n3. 搜索 openclash...")
    stdin, stdout, stderr = client.exec_command("opkg list | grep -i openclash")
    print(stdout.read().decode('utf-8', errors='ignore') or '无结果')
    
    # 安装
    print("\n4. 安装...")
    stdin, stdout, stderr = client.exec_command("opkg install luci-app-openclash 2>&1")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查结果
    print("\n5. 检查结果...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '成功' || echo '失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
