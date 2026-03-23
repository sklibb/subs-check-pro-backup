#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查服务状态
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 检查服务状态 ===")
    
    # 检查容器状态
    print("\n1. 容器状态...")
    stdin, stdout, stderr = client.exec_command("docker ps -a --filter name=subs-check-pro")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查端口监听
    print("\n2. 端口监听...")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp | grep -E '8199|8299'")
    print(stdout.read().decode('utf-8', errors='ignore') or "端口未监听")
    
    # 检查容器日志
    print("\n3. 容器日志...")
    stdin, stdout, stderr = client.exec_command("docker logs subs-check-pro --tail 20 2>&1")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 测试本地访问
    print("\n4. 测试本地访问...")
    stdin, stdout, stderr = client.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8299/admin 2>&1")
    print(f"HTTP 状态码: {stdout.read().decode('utf-8', errors='ignore').strip()}")
    
    stdin, stdout, stderr = client.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8199/admin 2>&1")
    print(f"HTTP 状态码 (8199): {stdout.read().decode('utf-8', errors='ignore').strip()}")
    
    client.close()


if __name__ == "__main__":
    main()
