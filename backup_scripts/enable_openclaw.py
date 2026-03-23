#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启用 OpenClaw 代理端口并重启
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 启用 OpenClaw ===")
    
    # 启用 OpenClaw
    print("1. 启用 OpenClaw 服务...")
    stdin, stdout, stderr = client.exec_command("uci set openclash.config.enable='1'")
    stdout.channel.recv_exit_status()
    
    print("2. 保存配置...")
    stdin, stdout, stderr = client.exec_command("uci commit openclash")
    stdout.channel.recv_exit_status()
    
    print("3. 重启 OpenClaw...")
    stdin, stdout, stderr = client.exec_command("/etc/init.d/openclash restart")
    stdout.channel.recv_exit_status()
    
    print("\n等待服务启动...")
    import time
    time.sleep(10)
    
    print("\n=== 检查代理端口 ===")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp | grep -E '7890|7891|7893'")
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output if output.strip() else "代理端口仍未监听")
    
    print("\n=== 测试代理 ===")
    stdin, stdout, stderr = client.exec_command("curl -x http://127.0.0.1:7890 -s -o /dev/null -w '%{http_code}' --connect-timeout 10 https://www.google.com 2>/dev/null || echo 'FAILED'")
    result = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"Google 访问结果: {result}")
    
    client.close()


if __name__ == "__main__":
    main()
