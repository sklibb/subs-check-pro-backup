#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查路由器代理环境
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 检查代理端口 ===")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp 2>/dev/null | grep -E '7890|7891|1080|8080|10808' || ss -tlnp 2>/dev/null | grep -E '7890|7891|1080|8080|10808'")
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output if output.strip() else "未发现常见代理端口")
    
    print("\n=== OpenClaw 容器 ===")
    stdin, stdout, stderr = client.exec_command("docker ps --filter name=openclaw --format '{{.Names}}: {{.Ports}}'")
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output if output.strip() else "未发现 openclaw 容器")
    
    print("\n=== 检查 Docker 网络 ===")
    stdin, stdout, stderr = client.exec_command("docker network ls")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 检查容器 IP ===")
    stdin, stdout, stderr = client.exec_command("docker inspect subs-check-pro --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'")
    subs_ip = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"subs-check-pro IP: {subs_ip}")
    
    stdin, stdout, stderr = client.exec_command("docker inspect openclaw --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'")
    openclaw_ip = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"openclaw IP: {openclaw_ip}")
    
    client.close()


if __name__ == "__main__":
    main()
