#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恢复 OpenClash
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 恢复 OpenClash ===")
    
    # 检查 OpenClash 是否还在
    print("\n1. 检查 OpenClash 状态...")
    stdin, stdout, stderr = client.exec_command("ls /usr/share/openclash 2>/dev/null || echo '不存在'")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(f"/usr/share/openclash: {result.strip()}")
    
    stdin, stdout, stderr = client.exec_command("opkg list-installed | grep openclash")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(f"已安装的包: {result.strip() or '无'}")
    
    # 检查 init.d
    print("\n2. 检查 init.d...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null || echo '不存在'")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(f"init.d 脚本: {result.strip()}")
    
    # 重新安装 OpenClash
    print("\n3. 重新安装 OpenClash...")
    stdin, stdout, stderr = client.exec_command("opkg update && opkg install luci-app-openclash --force-reinstall 2>&1")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(result)
    
    # 检查安装结果
    print("\n4. 检查安装结果...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '安装成功' || echo '安装失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
