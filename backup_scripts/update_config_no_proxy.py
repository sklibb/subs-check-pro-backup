#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新配置移除代理设置
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 更新配置 ===")
    
    # 移除代理设置
    print("\n1. 移除代理设置...")
    stdin, stdout, stderr = client.exec_command("sed -i 's/^system-proxy:.*/system-proxy: \"\"/' /opt/subs-check-pro/config/config.yaml")
    stdout.channel.recv_exit_status()
    
    # 验证修改
    print("\n2. 验证配置:")
    stdin, stdout, stderr = client.exec_command("grep 'system-proxy' /opt/subs-check-pro/config/config.yaml")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 重启容器
    print("\n3. 重启容器...")
    stdin, stdout, stderr = client.exec_command("docker restart subs-check-pro")
    stdout.channel.recv_exit_status()
    print("已重启")
    
    import time
    time.sleep(5)
    
    # 查看日志
    print("\n4. 查看启动日志:")
    stdin, stdout, stderr = client.exec_command("docker logs subs-check-pro --tail 20 2>&1")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
