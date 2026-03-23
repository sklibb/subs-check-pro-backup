#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传配置文件到路由器
"""

import paramiko
import sys

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"
LOCAL_CONFIG = r"C:\Users\Aaron\.rong\subs-check-pro-2.2.1_Windows_x86_64\config\config.yaml"
REMOTE_CONFIG = "/opt/subs-check-pro/config/config.yaml"


def main():
    print("=" * 60)
    print("上传配置文件到路由器")
    print("=" * 60)
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"\n[连接] 正在连接到 {ROUTER_HOST}...")
        client.connect(
            hostname=ROUTER_HOST,
            username=ROUTER_USER,
            password=ROUTER_PASSWORD,
            timeout=30,
            allow_agent=False,
            look_for_keys=False
        )
        print("[成功] SSH 连接成功!")
        
        sftp = client.open_sftp()
        
        print(f"\n[上传] {LOCAL_CONFIG}")
        print(f"[目标] {REMOTE_CONFIG}")
        
        sftp.put(LOCAL_CONFIG, REMOTE_CONFIG)
        print("[成功] 配置文件上传完成!")
        
        sftp.close()
        
        print("\n[重启] 重启容器以应用新配置...")
        stdin, stdout, stderr = client.exec_command("docker restart subs-check-pro")
        stdout.channel.recv_exit_status()
        print("[成功] 容器已重启")
        
        print("\n[完成] 配置已更新，容器已重启")
        print(f"Web 管理界面: http://{ROUTER_HOST}:8299")
        
    except FileNotFoundError:
        print(f"[错误] 本地配置文件不存在: {LOCAL_CONFIG}")
        sys.exit(1)
    except paramiko.AuthenticationException:
        print("[错误] 认证失败，请检查用户名和密码")
        sys.exit(1)
    except Exception as e:
        print(f"[错误] {e}")
        sys.exit(1)
    finally:
        client.close()
        print("\n[断开] SSH 连接已关闭")


if __name__ == "__main__":
    main()
