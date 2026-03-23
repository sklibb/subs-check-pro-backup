#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用国内镜像安装 OpenClash
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 使用国内镜像安装 OpenClash ===")
    
    # 清理
    print("\n1. 清理旧文件...")
    stdin, stdout, stderr = client.exec_command("rm -rf /tmp/openclash /tmp/luci-app-openclash*.ipk 2>/dev/null")
    stdout.channel.recv_exit_status()
    
    # 使用 jsdelivr CDN 下载
    print("\n2. 从 jsdelivr 下载...")
    stdin, stdout, stderr = client.exec_command("wget --no-check-certificate -O /tmp/luci-app-openclash.ipk 'https://fastly.jsdelivr.net/gh/vernesong/OpenClash@master/luci-app-openclash_0.47.071-r2_all.ipk' 2>&1 | tail -10")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查文件大小
    print("\n3. 检查文件大小...")
    stdin, stdout, stderr = client.exec_command("ls -lh /tmp/luci-app-openclash.ipk 2>/dev/null")
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
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '成功' || echo '失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
