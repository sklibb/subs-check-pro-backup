#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 Docker 容器网络
"""

import paramiko

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ROUTER_HOST, username=ROUTER_USER, password=ROUTER_PASSWORD, timeout=30, allow_agent=False, look_for_keys=False)
    
    print("=== 修复 Docker 容器网络 ===")
    
    # 检查 Docker DNS 配置
    print("\n1. 检查 Docker DNS 配置...")
    stdin, stdout, stderr = client.exec_command("cat /etc/docker/daemon.json 2>/dev/null || echo 'No daemon.json'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 检查容器 DNS
    print("\n2. 检查容器 DNS...")
    stdin, stdout, stderr = client.exec_command("docker exec subs-check-pro cat /etc/resolv.conf 2>&1")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 使用 host 网络模式重新创建容器
    print("\n3. 使用 host 网络模式重新创建容器...")
    
    # 停止并删除旧容器
    stdin, stdout, stderr = client.exec_command("docker stop subs-check-pro 2>/dev/null; docker rm subs-check-pro 2>/dev/null")
    stdout.channel.recv_exit_status()
    print("旧容器已删除")
    
    # 创建新容器（使用 host 网络模式）
    print("\n创建新容器...")
    cmd = """docker run -d \
  --name subs-check-pro \
  --restart always \
  --network host \
  -v /opt/subs-check-pro/config:/app/config \
  -v /opt/subs-check-pro/output:/app/output \
  -e TZ=Asia/Shanghai \
  -e LOG_LEVEL=info \
  ghcr.io/sinspired/subs-check-pro:latest"""
    
    stdin, stdout, stderr = client.exec_command(cmd)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    
    if error:
        print(f"错误: {error}")
    else:
        print(f"容器 ID: {output[:12]}")
    
    import time
    time.sleep(5)
    
    # 检查新容器状态
    print("\n4. 检查新容器状态...")
    stdin, stdout, stderr = client.exec_command("docker ps --filter name=subs-check-pro --format '{{.Names}}: {{.Status}}'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    # 测试容器网络
    print("\n5. 测试容器网络...")
    stdin, stdout, stderr = client.exec_command("docker exec subs-check-pro wget -q -O - --timeout=10 http://ip.sb 2>&1")
    result = stdout.read().decode('utf-8', errors='ignore')
    print(f"容器 IP: {result.strip() if result.strip() else '获取失败'}")
    
    # 查看日志
    print("\n6. 查看启动日志...")
    stdin, stdout, stderr = client.exec_command("docker logs subs-check-pro --tail 15 2>&1")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    client.close()


if __name__ == "__main__":
    main()
