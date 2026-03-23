#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清除锁并重新安装 OpenClash
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
    
    print("=== 清除锁并重新安装 OpenClash ===")
    
    # 清除锁和旧文件
    print("\n1. 清除锁和旧文件...")
    stdin, stdout, stderr = client.exec_command("rm -rf /var/lock/opkg.lock /tmp/opkg-* 2>/dev/null; killall wget opkg 2>/dev/null; sleep 2")
    stdout.channel.recv_exit_status()
    print("已清除")
    
    # 更新包列表
    print("\n2. 更新包列表...")
    stdin, stdout, stderr = client.exec_command("opkg update 2>&1 | tail -3")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 下载包
    print("\n3. 下载包...")
    stdin, stdout, stderr = client.exec_command("opkg download luci-app-openclash 2>&1")
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
    
    # 检查下载的文件
    print("\n4. 检查下载的文件...")
    stdin, stdout, stderr = client.exec_command("ls -lh /tmp/opkg-*/luci-app-openclash*.ipk 2>/dev/null")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(result or '无')
    
    # 检查 MD5
    print("\n5. 检查 MD5...")
    stdin, stdout, stderr = client.exec_command("md5sum /tmp/opkg-*/luci-app-openclash*.ipk 2>/dev/null")
    print(stdout.read().decode('utf-8', errors='ignore') or '无法计算')
    
    # 安装
    print("\n6. 安装...")
    stdin, stdout, stderr = client.exec_command("opkg install luci-app-openclash 2>&1")
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    print(output)
    if error:
        print(f"错误：{error}")
    
    # 检查结果
    print("\n7. 检查结果...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '成功' || echo '失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
