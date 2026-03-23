#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过源码安装 OpenClash
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 源码安装 OpenClash ===")
    
    # 清理
    print("\n1. 清理旧文件...")
    stdin, stdout, stderr = client.exec_command("rm -rf /tmp/openclash 2>/dev/null")
    stdout.channel.recv_exit_status()
    
    # 下载源码
    print("\n2. 下载源码...")
    stdin, stdout, stderr = client.exec_command("cd /tmp && git clone --depth 1 https://github.com/vernesong/OpenClash.git 2>&1 | tail -5")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 安装
    print("\n3. 安装...")
    stdin, stdout, stderr = client.exec_command("cd /tmp/OpenClash && bash install.sh 2>&1 | tail -20")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查结果
    print("\n4. 检查结果...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '成功' || echo '失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    stdin, stdout, stderr = client.exec_command("ls /usr/share/openclash 2>/dev/null && echo '存在' || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
