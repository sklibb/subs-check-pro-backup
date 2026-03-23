#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卸载 OpenClaw
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
    
    print("=== 卸载 OpenClaw ===")
    
    # 停止 OpenClaw
    print("\n1. 停止 OpenClaw 服务...")
    stdin, stdout, stderr = client.exec_command("/etc/init.d/openclash stop 2>/dev/null; killall clash 2>/dev/null; killall openclaw 2>/dev/null; killall openclaw-gateway 2>/dev/null")
    stdout.channel.recv_exit_status()
    print("已停止")
    
    # 禁用开机启动
    print("\n2. 禁用开机启动...")
    stdin, stdout, stderr = client.exec_command("/etc/init.d/openclash disable 2>/dev/null")
    stdout.channel.recv_exit_status()
    print("已禁用")
    
    # 删除 OpenClaw
    print("\n3. 删除 OpenClaw 文件...")
    stdin, stdout, stderr = client.exec_command("rm -rf /etc/openclash /etc/config/openclash /etc/init.d/openclash /usr/share/openclash /www/luci-static/openclash 2>/dev/null")
    stdout.channel.recv_exit_status()
    print("已删除配置文件")
    
    # 删除 Docker 容器
    print("\n4. 删除 OpenClaw Docker 容器...")
    stdin, stdout, stderr = client.exec_command("docker stop openclaw 2>/dev/null; docker rm openclaw 2>/dev/null")
    stdout.channel.recv_exit_status()
    print("已删除容器")
    
    # 检查结果
    print("\n5. 检查卸载结果...")
    stdin, stdout, stderr = client.exec_command("which clash 2>/dev/null; which openclaw 2>/dev/null; ls /etc/openclash 2>/dev/null")
    result = stdout.read().decode('utf-8', errors='ignore')
    if result.strip():
        print(f"残留文件: {result}")
    else:
        print("OpenClaw 已完全卸载")
    
    # 检查端口
    print("\n6. 检查端口释放...")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp | grep -E '7890|7891|7893|9090' 2>/dev/null")
    result = stdout.read().decode('utf-8', errors='ignore')
    if result.strip():
        print(f"端口仍被占用:\n{result}")
    else:
        print("代理端口已释放")
    
    print("\n=== 卸载完成 ===")
    
    client.close()


if __name__ == "__main__":
    main()
