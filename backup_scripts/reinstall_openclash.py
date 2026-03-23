#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制重装 OpenClash
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 强制重装 OpenClash ===")
    
    # 强制重装
    print("\n1. 强制重装...")
    stdin, stdout, stderr = client.exec_command("opkg install --force-reinstall luci-app-openclash 2>&1")
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    print(output)
    if error:
        print(f"错误: {error}")
    
    # 检查结果
    print("\n2. 检查安装结果...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '安装成功' || echo '安装失败'")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(result)
    
    stdin, stdout, stderr = client.exec_command("ls /etc/openclash 2>/dev/null && echo '配置目录存在' || echo '配置目录不存在'")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(result)
    
    # 启用服务
    print("\n3. 启用服务...")
    stdin, stdout, stderr = client.exec_command("/etc/init.d/openclash enable 2>/dev/null; /etc/init.d/openclash start 2>/dev/null")
    stdout.channel.recv_exit_status()
    print("已尝试启动")
    
    import time
    time.sleep(3)
    
    # 检查状态
    print("\n4. 检查服务状态...")
    stdin, stdout, stderr = client.exec_command("ps | grep clash | grep -v grep")
    print(stdout.read().decode('utf-8', errors='ignore') or "未运行")
    
    client.close()


if __name__ == "__main__":
    main()
