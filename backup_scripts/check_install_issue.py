#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查安装卡住的原因
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 检查安装状态 ===")
    
    # 检查下载文件
    print("\n1. 检查下载文件...")
    stdin, stdout, stderr = client.exec_command("ls -la /tmp/opkg-*/luci-app-openclash* 2>/dev/null || echo '无下载文件'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查网络连接
    print("\n2. 检查网络...")
    stdin, stdout, stderr = client.exec_command("curl -s --connect-timeout 5 -o /dev/null -w '%{http_code}' https://github.com 2>&1")
    print(f"GitHub 访问: {stdout.read().decode('utf-8', errors='ignore').strip()}")
    
    # 检查 opkg 锁
    print("\n3. 检查 opkg 锁...")
    stdin, stdout, stderr = client.exec_command("ls -la /var/lock/opkg.lock 2>/dev/null || echo '无锁'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 尝试清除锁并重新安装
    print("\n4. 清除锁并重新安装...")
    stdin, stdout, stderr = client.exec_command("rm -f /var/lock/opkg.lock 2>/dev/null; killall opkg wget 2>/dev/null; sleep 2; opkg install --force-reinstall luci-app-openclash 2>&1 &")
    print("已清除锁并重新启动安装")
    
    client.close()


if __name__ == "__main__":
    main()
