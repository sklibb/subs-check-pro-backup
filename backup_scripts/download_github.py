#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 GitHub 下载 OpenClash (最新版)
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 下载 OpenClash 最新版 ===")
    
    # 清理旧文件
    print("\n1. 清理旧文件...")
    stdin, stdout, stderr = client.exec_command("rm -rf /tmp/opkg-* /tmp/luci-app-openclash*.ipk 2>/dev/null")
    stdout.channel.recv_exit_status()
    print("已清理")
    
    # 从 GitHub 下载最新版
    print("\n2. 从 GitHub 下载...")
    stdin, stdout, stderr = client.exec_command("wget --no-check-certificate -O /tmp/luci-app-openclash.ipk 'https://github.com/vernesong/OpenClash/releases/download/prerelease/luci-app-openclash_0.47.071-r2_all.ipk' 2>&1")
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
    
    # 检查文件大小
    print("\n3. 检查文件大小...")
    stdin, stdout, stderr = client.exec_command("ls -lh /tmp/luci-app-openclash.ipk 2>/dev/null || echo '下载失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 安装
    print("\n4. 安装...")
    stdin, stdout, stderr = client.exec_command("opkg install /tmp/luci-app-openclash.ipk 2>&1")
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    print(output)
    if error:
        print(f"错误：{error}")
    
    # 检查结果
    print("\n5. 检查结果...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '安装成功' || echo '安装失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
