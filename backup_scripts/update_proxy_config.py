#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新配置并重启容器
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"
PROXY_USER = "Clash"
PROXY_PASS = "vLzYmzrv"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 更新配置文件 ===")
    
    # 更新 system-proxy 配置
    proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@172.17.0.1:7890"
    print(f"设置代理: {proxy_url}")
    
    cmd = f"sed -i 's|^system-proxy:.*|system-proxy: \"{proxy_url}\"|' /opt/subs-check-pro/config/config.yaml"
    stdin, stdout, stderr = client.exec_command(cmd)
    stdout.channel.recv_exit_status()
    
    # 验证修改
    print("\n验证配置:")
    stdin, stdout, stderr = client.exec_command("grep 'system-proxy' /opt/subs-check-pro/config/config.yaml")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 重启容器
    print("\n重启容器...")
    stdin, stdout, stderr = client.exec_command("docker restart subs-check-pro")
    stdout.channel.recv_exit_status()
    
    print("\n等待容器启动...")
    import time
    time.sleep(5)
    
    print("\n查看日志:")
    stdin, stdout, stderr = client.exec_command("docker logs subs-check-pro --tail 20")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
