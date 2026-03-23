#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 OpenClaw 配置
"""

import paramiko
import json

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== OpenClaw 容器详情 ===")
    stdin, stdout, stderr = client.exec_command("docker inspect openclaw")
    output = stdout.read().decode('utf-8', errors='ignore')
    
    try:
        data = json.loads(output)
        if data:
            container = data[0]
            print(f"名称: {container.get('Name', 'N/A')}")
            print(f"状态: {container.get('State', {}).get('Status', 'N/A')}")
            print(f"网络模式: {container.get('HostConfig', {}).get('NetworkMode', 'N/A')}")
            
            ports = container.get('NetworkSettings', {}).get('Ports', {})
            print(f"端口映射: {ports if ports else '无'}")
            
            env = container.get('Config', {}).get('Env', [])
            print("\n环境变量:")
            for e in env:
                if any(x in e.upper() for x in ['PROXY', 'PORT', 'SOCKS', 'HTTP', 'MIXED']):
                    print(f"  {e}")
    except:
        print(output[:500])
    
    print("\n=== 检查监听端口 ===")
    stdin, stdout, stderr = client.exec_command("ss -tlnp | head -20")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 检查 127.0.0.1 端口 ===")
    stdin, stdout, stderr = client.exec_command("ss -tlnp | grep 127.0.0.1")
    print(stdout.read().decode('utf-8', errors='ignore') or "无")
    
    client.close()


if __name__ == "__main__":
    main()
