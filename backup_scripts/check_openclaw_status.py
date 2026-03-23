#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 OpenClaw 运行状态
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== OpenClaw 进程状态 ===")
    stdin, stdout, stderr = client.exec_command("ps | grep -E 'clash|openclaw' | grep -v grep")
    print(stdout.read().decode('utf-8', errors='ignore') or "无进程")
    
    print("\n=== OpenClaw 服务状态 ===")
    stdin, stdout, stderr = client.exec_command("/etc/init.d/openclash status 2>/dev/null || echo 'status command not available'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n=== 检查代理端口监听 ===")
    stdin, stdout, stderr = client.exec_command("netstat -tlnp | grep -E '7890|7891|7892|7893|7895'")
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output if output.strip() else "代理端口未监听!")
    
    print("\n=== OpenClaw 日志 (最后20行) ===")
    stdin, stdout, stderr = client.exec_command("logread | grep -i openclash | tail -20")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
