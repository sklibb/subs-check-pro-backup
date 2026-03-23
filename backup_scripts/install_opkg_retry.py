#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 opkg 默认源重新安装
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
    
    print("=== 使用 opkg 默认源重新安装 ===")
    
    # 清理
    print("\n1. 清理旧文件和锁...")
    stdin, stdout, stderr = client.exec_command("rm -rf /tmp/opkg-* /var/lock/opkg.lock 2>/dev/null")
    stdout.channel.recv_exit_status()
    print("已清理")
    
    # 更新包列表
    print("\n2. 更新包列表...")
    stdin, stdout, stderr = client.exec_command("opkg update 2>&1 | tail -3")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 重新安装（多次尝试）
    for i in range(3):
        print(f"\n{i+1}. 尝试安装...")
        stdin, stdout, stderr = client.exec_command("opkg install luci-app-openclash 2>&1")
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        # 检查结果
        stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null")
        if stdout.read().decode('utf-8', errors='ignore').strip():
            print("安装成功!")
            break
        
        print(f"尝试 {i+1} 失败，等待 10 秒后重试...")
        time.sleep(10)
    
    # 最终检查
    print("\n3. 最终检查...")
    stdin, stdout, stderr = client.exec_command("ls /etc/init.d/openclash 2>/dev/null && echo '成功' || echo '失败'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    stdin, stdout, stderr = client.exec_command("ls /usr/share/openclash 2>/dev/null && echo '存在' || echo '不存在'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
