#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用多个镜像源安装 OpenClash
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 使用多个镜像源安装 OpenClash ===")
    
    # 清理
    print("\n1. 清理旧文件...")
    stdin, stdout, stderr = client.exec_command("rm -rf /tmp/openclash /tmp/luci-app-openclash*.ipk 2>/dev/null")
    stdout.channel.recv_exit_status()
    
    # 尝试多个镜像源
    mirrors = [
        "https://raw.githubusercontent.com/vernesong/OpenClash/master/luci-app-openclash_0.47.071-r2_all.ipk",
        "https://cdn.jsdelivr.net/gh/vernesong/OpenClash@master/luci-app-openclash_0.47.071-r2_all.ipk",
        "http://luci-app-openclash.1234567890.xyz/luci-app-openclash_0.47.071-r2_all.ipk"
    ]
    
    for i, mirror in enumerate(mirrors, 1):
        print(f"\n{i}. 尝试镜像：{mirror[:60]}...")
        stdin, stdout, stderr = client.exec_command(f"wget --no-check-certificate --timeout=30 -O /tmp/luci-app-openclash.ipk '{mirror}' 2>&1 | tail -5")
        result = stdout.read().decode('utf-8', errors='ignore')
        print(result)
        
        # 检查文件大小
        stdin, stdout, stderr = client.exec_command("ls -l /tmp/luci-app-openclash.ipk 2>/dev/null | awk '{{print $5}}'")
        size = int(stdout.read().decode('utf-8', errors='ignore').strip() or 0)
        
        if size > 100000:  # 大于 100KB
            print(f"下载成功！文件大小：{size} bytes")
            break
        else:
            print(f"下载失败，文件大小：{size} bytes")
    
    # 检查最终文件
    print("\n2. 检查最终文件...")
    stdin, stdout, stderr = client.exec_command("ls -lh /tmp/luci-app-openclash.ipk 2>/dev/null")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 安装
    print("\n3. 安装...")
    stdin, stdout, stderr = client.exec_command("opkg install /tmp/luci-app-openclash.ipk 2>&1")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查结果
    print("\n4. 检查结果...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '成功' || echo '失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
