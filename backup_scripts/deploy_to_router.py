#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Subs-Check Pro Docker 部署脚本
用于在 OpenWrt 路由器上部署 subs-check-pro 容器
"""

import paramiko
import time
import sys

ROUTER_HOST = "192.168.2.1"
ROUTER_USER = "root"
ROUTER_PASSWORD = "admin"
CONTAINER_NAME = "subs-check-pro"
IMAGE_NAME = "ghcr.io/sinspired/subs-check-pro:latest"


def create_ssh_client():
    """创建 SSH 连接"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"[连接] 正在连接到 {ROUTER_HOST}...")
        client.connect(
            hostname=ROUTER_HOST,
            username=ROUTER_USER,
            password=ROUTER_PASSWORD,
            timeout=30,
            allow_agent=False,
            look_for_keys=False
        )
        print("[成功] SSH 连接成功!")
        return client
    except paramiko.AuthenticationException:
        print("[错误] 认证失败，请检查用户名和密码")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"[错误] SSH 连接失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[错误] 连接异常: {e}")
        sys.exit(1)


def run_command(client, command, show_output=True):
    """执行远程命令"""
    if show_output:
        print(f"[执行] {command}")
    
    stdin, stdout, stderr = client.exec_command(command)
    
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    
    if show_output and output:
        print(output.rstrip())
    if error and exit_code != 0:
        print(f"[错误] {error.rstrip()}")
    
    return exit_code, output, error


def check_docker(client):
    """检查 Docker 环境"""
    print("\n[检查] Docker 环境...")
    
    exit_code, output, _ = run_command(client, "docker --version")
    if exit_code != 0:
        print("[错误] Docker 未安装或无法运行")
        return False
    
    print(f"[信息] {output.strip()}")
    
    exit_code, output, _ = run_command(client, "docker ps")
    if exit_code != 0:
        print("[错误] Docker 服务未运行")
        return False
    
    return True


def check_existing_container(client):
    """检查是否已存在容器"""
    exit_code, output, _ = run_command(
        client, 
        f"docker ps -a --filter name={CONTAINER_NAME} --format '{{{{.Names}}}}'",
        show_output=False
    )
    return CONTAINER_NAME in output


def stop_and_remove_container(client):
    """停止并删除现有容器"""
    print(f"\n[清理] 停止并删除现有容器 {CONTAINER_NAME}...")
    run_command(client, f"docker stop {CONTAINER_NAME} 2>/dev/null", show_output=False)
    run_command(client, f"docker rm {CONTAINER_NAME} 2>/dev/null", show_output=False)


def pull_image(client):
    """拉取 Docker 镜像"""
    print(f"\n[拉取] 正在拉取镜像 {IMAGE_NAME}...")
    print("[提示] 这可能需要几分钟，请耐心等待...")
    
    exit_code, _, _ = run_command(client, f"docker pull {IMAGE_NAME}")
    
    if exit_code != 0:
        print("[警告] 拉取镜像失败，尝试使用本地镜像...")
        return False
    
    return True


def create_directories(client):
    """创建必要的目录"""
    print("\n[准备] 创建配置和数据目录...")
    run_command(client, "mkdir -p /opt/subs-check-pro/config")
    run_command(client, "mkdir -p /opt/subs-check-pro/output")


def create_default_config(client):
    """创建默认配置文件"""
    print("\n[配置] 检查配置文件...")
    
    exit_code, _, _ = run_command(
        client,
        "test -f /opt/subs-check-pro/config/config.yaml",
        show_output=False
    )
    
    if exit_code != 0:
        print("[配置] 创建默认配置文件...")
        config_content = """# Subs-Check Pro 配置文件
# 请在此处添加你的订阅链接

server:
  port: 8299
  sub-store-port: 8199

subscriptions: []
# subscriptions:
#   - "你的订阅链接1"
#   - "你的订阅链接2"

check:
  concurrency: 100
  timeout: 10
  speed-test: true
  media-test: true

output:
  save-yaml: true
  save-base64: true
"""
        run_command(
            client,
            f"cat > /opt/subs-check-pro/config/config.yaml << 'EOF'\n{config_content}\nEOF"
        )
        print("[配置] 配置文件已创建，请通过 Web 界面修改")


def deploy_container(client):
    """部署容器"""
    print(f"\n[部署] 启动容器 {CONTAINER_NAME}...")
    
    deploy_cmd = f"""docker run -d \\
  --name {CONTAINER_NAME} \\
  --restart always \\
  -p 8299:8299 \\
  -p 8199:8199 \\
  -v /opt/subs-check-pro/config:/app/config \\
  -v /opt/subs-check-pro/output:/app/output \\
  -e TZ=Asia/Shanghai \\
  -e LOG_LEVEL=info \\
  {IMAGE_NAME}"""
    
    exit_code, output, _ = run_command(client, deploy_cmd)
    
    if exit_code != 0:
        print("[错误] 容器启动失败")
        return False
    
    return True


def verify_deployment(client):
    """验证部署"""
    print("\n[验证] 检查容器状态...")
    
    time.sleep(3)
    
    exit_code, output, _ = run_command(
        client,
        f"docker ps --filter name={CONTAINER_NAME} --format 'table {{{{.Names}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}'"
    )
    
    if exit_code != 0 or not output.strip():
        print("[错误] 容器未运行")
        run_command(client, f"docker logs {CONTAINER_NAME} --tail 50")
        return False
    
    print("\n[成功] 部署完成!")
    print("=" * 60)
    print(f"Web 管理界面: http://{ROUTER_HOST}:8299")
    print(f"Sub-Store 服务: http://{ROUTER_HOST}:8199")
    print("=" * 60)
    
    return True


def show_logs(client):
    """显示容器日志"""
    print("\n[日志] 容器启动日志:")
    run_command(client, f"docker logs {CONTAINER_NAME} --tail 30")


def main():
    """主函数"""
    print("=" * 60)
    print("Subs-Check Pro Docker 部署脚本")
    print("=" * 60)
    
    client = None
    
    try:
        client = create_ssh_client()
        
        if not check_docker(client):
            print("\n[失败] Docker 环境检查失败")
            return
        
        if check_existing_container(client):
            stop_and_remove_container(client)
        
        pull_image(client)
        create_directories(client)
        create_default_config(client)
        
        if not deploy_container(client):
            print("\n[失败] 容器部署失败")
            return
        
        verify_deployment(client)
        show_logs(client)
        
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消操作")
    except Exception as e:
        print(f"\n[异常] {e}")
    finally:
        if client:
            client.close()
            print("\n[断开] SSH 连接已关闭")


if __name__ == "__main__":
    main()
