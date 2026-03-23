#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNS服务器Ping测试脚本
从网页提取DNS服务器地址，执行多轮ping测试，并输出延迟最低的DNS服务器
"""

import re
import subprocess
import platform
import statistics
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Optional
import time


@dataclass
class DNSTestResult:
    """DNS测试结果数据类"""
    ip: str
    latencies: List[float] = field(default_factory=list)
    packet_loss: int = 0
    total_tests: int = 0
    
    @property
    def avg_latency(self) -> Optional[float]:
        """计算平均延迟"""
        if self.latencies:
            return statistics.mean(self.latencies)
        return None
    
    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.total_tests == 0:
            return 0.0
        return (len(self.latencies) / self.total_tests) * 100


def fetch_dns_from_webpage(url: str) -> List[str]:
    """
    从网页提取DNS服务器IP地址
    
    Args:
        url: 目标网页URL
        
    Returns:
        DNS服务器IP地址列表
    """
    print(f"正在从网页获取DNS服务器列表: {url}")
    
    try:
        request = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response = urlopen(request, timeout=30)
        html_content = response.read().decode('utf-8', errors='ignore')
    except (URLError, HTTPError) as e:
        print(f"获取网页内容失败: {e}")
        return []
    
    ipv4_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    
    all_ips = re.findall(ipv4_pattern, html_content)
    
    dns_servers = []
    seen = set()
    
    for ip in all_ips:
        if ip not in seen:
            seen.add(ip)
            dns_servers.append(ip)
    
    print(f"共提取到 {len(dns_servers)} 个DNS服务器地址")
    return dns_servers


def ping_dns(ip: str, count: int = 5, timeout: int = 2) -> List[Optional[float]]:
    """
    对DNS服务器执行ping测试
    
    Args:
        ip: 目标IP地址
        count: ping次数
        timeout: 超时时间(秒)
        
    Returns:
        延迟列表(毫秒)，超时或失败为None
    """
    latencies = []
    
    system = platform.system().lower()
    
    if system == 'windows':
        cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), ip]
    else:
        cmd = ['ping', '-c', str(count), '-W', str(timeout), ip]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=count * timeout + 10,
            creationflags=subprocess.CREATE_NO_WINDOW if system == 'windows' else 0
        )
        
        output = result.stdout
        
        if system == 'windows':
            time_pattern = r'时间[=<](\d+)ms|time[=<](\d+)ms'
            matches = re.findall(time_pattern, output, re.IGNORECASE)
            for match in matches:
                latency = float(match[0] if match[0] else match[1])
                latencies.append(latency)
        else:
            time_pattern = r'time=(\d+\.?\d*)\s*ms'
            matches = re.findall(time_pattern, output)
            for match in matches:
                latencies.append(float(match))
        
        while len(latencies) < count:
            latencies.append(None)
            
    except subprocess.TimeoutExpired:
        latencies = [None] * count
    except Exception as e:
        print(f"  ping {ip} 时发生错误: {e}")
        latencies = [None] * count
    
    return latencies


def test_dns_server(ip: str, rounds: int = 3, pings_per_round: int = 5) -> DNSTestResult:
    """
    对单个DNS服务器执行完整测试
    
    Args:
        ip: DNS服务器IP
        rounds: 测试轮数
        pings_per_round: 每轮ping次数
        
    Returns:
        测试结果
    """
    result = DNSTestResult(ip=ip)
    total_pings = rounds * pings_per_round
    result.total_tests = total_pings
    
    for round_num in range(1, rounds + 1):
        print(f"  DNS {ip} - 第 {round_num}/{rounds} 轮测试...", end='\r')
        latencies = ping_dns(ip, count=pings_per_round)
        
        for latency in latencies:
            if latency is not None:
                result.latencies.append(latency)
            else:
                result.packet_loss += 1
        
        if round_num < rounds:
            time.sleep(0.5)
    
    return result


def run_dns_tests(dns_servers: List[str], rounds: int = 3, pings_per_round: int = 5, 
                  max_workers: int = 10) -> List[DNSTestResult]:
    """
    并行执行DNS测试
    
    Args:
        dns_servers: DNS服务器列表
        rounds: 测试轮数
        pings_per_round: 每轮ping次数
        max_workers: 最大并行数
        
    Returns:
        测试结果列表
    """
    results = []
    total = len(dns_servers)
    
    print(f"\n开始测试 {total} 个DNS服务器...")
    print(f"测试配置: {rounds}轮 × {pings_per_round}次ping = 每个DNS共{rounds * pings_per_round}次测试")
    print("-" * 60)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {
            executor.submit(test_dns_server, ip, rounds, pings_per_round): ip 
            for ip in dns_servers
        }
        
        completed = 0
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                result = future.result()
                results.append(result)
                completed += 1
                
                if result.avg_latency is not None:
                    status = f"平均延迟: {result.avg_latency:.1f}ms, 成功率: {result.success_rate:.1f}%"
                else:
                    status = "无法连接"
                print(f"[{completed}/{total}] {ip}: {status}                    ")
            except Exception as e:
                print(f"[{completed}/{total}] {ip}: 测试失败 - {e}")
                results.append(DNSTestResult(ip=ip, total_tests=rounds * pings_per_round))
    
    return results


def analyze_results(results: List[DNSTestResult], top_n: int = 10) -> List[DNSTestResult]:
    """
    分析测试结果并排序
    
    Args:
        results: 测试结果列表
        top_n: 返回前N个结果
        
    Returns:
        排序后的前N个结果
    """
    valid_results = [r for r in results if r.avg_latency is not None]
    
    valid_results.sort(key=lambda x: x.avg_latency)
    
    return valid_results[:top_n]


PUBLIC_DNS_INFO = {
    "114.114.114.114": "114DNS",
    "114.114.115.115": "114DNS",
    "119.29.29.29": "DNSPod (腾讯)",
    "182.254.116.116": "DNSPod (腾讯)",
    "101.226.4.6": "DNS派 (电信/移动)",
    "218.30.118.6": "DNS派 (电信/移动)",
    "123.125.81.6": "DNS派 (联通)",
    "140.207.198.6": "DNS派 (联通)",
    "1.2.4.8": "CNNIC DNS",
    "210.2.4.8": "CNNIC DNS",
    "8.8.8.8": "Google DNS",
    "8.8.4.4": "Google DNS",
    "1.1.1.1": "Cloudflare DNS",
    "1.0.0.1": "Cloudflare DNS",
    "9.9.9.9": "Quad9 DNS",
    "149.112.112.112": "Quad9 DNS",
    "185.222.222.222": "DNS.SB",
    "185.184.222.222": "DNS.SB",
    "208.67.222.222": "OpenDNS",
    "208.67.220.220": "OpenDNS",
    "223.5.5.5": "阿里DNS",
    "223.6.6.6": "阿里DNS",
    "183.60.83.19": "腾讯DNS",
    "183.60.82.98": "腾讯DNS",
    "180.76.76.76": "百度DNS",
    "4.2.2.1": "微软DNS",
    "4.2.2.2": "微软DNS",
    "180.184.1.1": "字节跳动DNS",
    "180.184.2.2": "字节跳动DNS",
}


def print_results(top_results: List[DNSTestResult], all_results: List[DNSTestResult]):
    """
    打印测试结果
    
    Args:
        top_results: 排名前N的结果
        all_results: 所有测试结果
    """
    print("\n" + "=" * 70)
    print("DNS服务器测试结果 - 延迟最低的前10名")
    print("=" * 70)
    print(f"{'排名':<6}{'DNS服务器':<20}{'平均延迟':<15}{'成功率':<12}{'丢包数'}")
    print("-" * 70)
    
    for i, result in enumerate(top_results, 1):
        print(f"{i:<6}{result.ip:<20}{result.avg_latency:.2f}ms{'':<8}{result.success_rate:.1f}%{'':<7}{result.packet_loss}/{result.total_tests}")
    
    print("=" * 70)
    
    public_results = []
    for r in all_results:
        if r.ip in PUBLIC_DNS_INFO and r.avg_latency is not None:
            public_results.append(r)
    
    if public_results:
        public_results.sort(key=lambda x: x.avg_latency)
        
        print("\n" + "=" * 80)
        print("公共DNS服务器测试结果排名")
        print("=" * 80)
        print(f"{'排名':<6}{'DNS服务器':<20}{'服务商':<18}{'平均延迟':<12}{'成功率':<10}{'丢包数'}")
        print("-" * 80)
        
        for i, result in enumerate(public_results, 1):
            provider = PUBLIC_DNS_INFO.get(result.ip, "未知")
            print(f"{i:<6}{result.ip:<20}{provider:<18}{result.avg_latency:.2f}ms{'':<5}{result.success_rate:.1f}%{'':<5}{result.packet_loss}/{result.total_tests}")
        
        print("=" * 80)
    
    total_tested = len(all_results)
    valid_count = len([r for r in all_results if r.avg_latency is not None])
    failed_count = total_tested - valid_count
    
    print(f"\n统计摘要:")
    print(f"  总测试DNS数: {total_tested}")
    print(f"  可用DNS数: {valid_count}")
    print(f"  不可用DNS数: {failed_count}")
    print(f"  可用率: {(valid_count/total_tested*100):.1f}%" if total_tested > 0 else "  可用率: 0%")


def main():
    """主函数"""
    url = "https://dnsdaquan.com/"
    
    rounds = 3
    pings_per_round = 5
    top_n = 10
    max_workers = 15
    
    print("=" * 70)
    print("DNS服务器Ping测试工具")
    print("=" * 70)
    
    dns_servers = fetch_dns_from_webpage(url)
    
    if not dns_servers:
        print("未能获取到DNS服务器列表，使用预设列表...")
        dns_servers = [
            "114.114.114.114", "114.114.115.115",
            "119.29.29.29", "182.254.116.116",
            "101.226.4.6", "218.30.118.6",
            "123.125.81.6", "140.207.198.6",
            "1.2.4.8", "210.2.4.8",
            "8.8.8.8", "8.8.4.4",
            "1.1.1.1", "1.0.0.1",
            "9.9.9.9", "149.112.112.112",
            "185.222.222.222", "185.184.222.222",
            "208.67.222.222", "208.67.220.220",
            "223.5.5.5", "223.6.6.6",
            "183.60.83.19", "183.60.82.98",
            "180.76.76.76", "4.2.2.1", "4.2.2.2"
        ]
    
    results = run_dns_tests(dns_servers, rounds, pings_per_round, max_workers)
    
    top_results = analyze_results(results, top_n)
    
    print_results(top_results, results)
    
    print("\n测试完成!")


if __name__ == "__main__":
    main()
