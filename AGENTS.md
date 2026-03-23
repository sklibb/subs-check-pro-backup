# Subs-Check⁺ PRO 项目指南

## 项目概述

**Subs-Check⁺ PRO** 是一个高性能代理订阅检测工具，支持测活、测速、媒体解锁检测。该项目采用 Go 语言开发，支持 `100-1000` 高并发低占用运行，检测结果更准确。

### 主要特性

- 自适应流水线高并发模式
- 增强位置标签显示（支持国家代码转中文名称）
- 智能节点乱序
- 保存并加载历次可用节点
- 历史节点仅测活模式（跳过测速提升检测效率）
- 节点按下载速度降序排序
- 统计订阅链接总数、可用节点数量、成功率
- 自动检测代理环境
- 自动生成 mihomo 和 sing-box 订阅
- 集成 sub-store 前端和后端
- 支持一键复制分享
- 自动无缝版本更新
- 支持 Windows、Linux、macOS 多平台
- 支持 Docker 部署

### 技术栈

- **语言**: Go 1.26
- **核心库**:
  - `metacubex/mihomo` - 代理核心
  - `gin` - Web 框架
  - `maxminddb-golang` - GeoIP 数据库
  - `go-yaml` - YAML 配置解析
- **前端**: WebUI (集成 sub-store)

---

## 目录结构

```
subs-check-pro/
├── main.go              # 程序入口
├── init.go              # 初始化配置（日志、进程管理等）
├── app/                 # 主应用程序逻辑
│   ├── app.go           # 应用核心
│   ├── config.go        # 配置管理
│   ├── server.go        # HTTP 服务器
│   ├── embed.go         # 资源嵌入
│   ├── updater.go       # 版本更新
│   ├── monitor/         # 内存监控
│   ├── static/          # WebUI 静态文件
│   └── templates/       # HTML 模板
├── assets/              # 内置资源（订阅规则、GeoIP 数据库等）
├── check/               # 代理检测核心逻辑
│   ├── check.go        # 检测主流程
│   ├── progress.go     # 进度跟踪
│   ├── decay.go        # 衰减算法
│   └── platform/       # 各平台检测 (Netflix, YouTube, GPT 等)
├── proxy/               # 代理处理模块
│   ├── info.go         # 代理信息获取
│   ├── get.go          # 订阅获取
│   ├── dedup.go        # 去重
│   ├── rename.go       # 节点重命名
│   └── utils.go        # 工具函数
├── config/              # 配置模块
│   ├── config.go       # 配置解析
│   └── config.yaml.example  # 配置示例
├── save/                # 结果保存模块
│   ├── save.go         # 保存主逻辑
│   └── method/         # 保存方式 (local, r2, gist, webdav, s3)
├── utils/               # 工具函数
│   ├── notify.go       # 通知推送
│   ├── callback.go     # 回调脚本
│   ├── proxy.go        # 代理工具
│   └── updatesubs.go  # 订阅更新
└── docs-site/          # 文档站点 (Docusaurus)
```

---

## 构建和运行

### 环境要求

- Go 1.26+
- Node.js (用于构建静态资源，仅 Windows 构建需要)

### 构建命令

```bash
# 构建当前平台
make build

# 跨平台构建
make linux-amd64    # Linux x86_64
make linux-arm64    # Linux ARM64
make linux-arm      # Linux ARMv7
make windows-amd64  # Windows x86_64
make darwin-amd64   # macOS x86_64
make darwin-arm64   # macOS ARM64

# 构建所有平台
make build-all
```

### 运行命令

```bash
# 指定配置文件运行
./subs-check-pro.exe -f ./config/config.yaml

# Docker 运行
docker run -d \
  --name subs-check-pro \
  -p 8299:8299 \
  -p 8199:8199 \
  -v ./config:/app/config \
  -v ./output:/app/output \
  --restart always \
  ghcr.io/sinspired/subs-check-pro:latest
```

### 环境变量

| 变量 | 说明 |
|------|------|
| `LOG_LEVEL` | 日志级别 (debug/info/warn/error) |
| `MIHOMO_DEBUG` | 设为非空启用 mihomo 调试日志 |
| `SUB_CHECK_PPROF` | 设为非空启用 pprof 服务器 (:61000) |
| `HTTP_PROXY` / `HTTPS_PROXY` | HTTP 代理（加速订阅拉取） |
| `START_FROM_GUI` | 设为 "true" 禁用自动更新 |
| `RUNNING_IN_DOCKER` | 设为 "true" 强制识别为 Docker 环境 |

### 构建与测试规范

#### 构建规范
1. **禁止在工作区目录生成exe文件**：所有编译产物不得直接生成在项目工作区目录下
2. **统一输出路径**：所有编译产物必须输出至指定路径：`C:\Users\Aaron\.rong\subs-check-pro-2.2.1_Windows_x86_64`
3. **编译命令**：使用以下命令进行编译
   ```bash
   # 构建并输出到指定目录
   go build -o "C:\Users\Aaron\.rong\subs-check-pro-2.2.1_Windows_x86_64\subs-check-pro.exe"
   ```

#### 测试规范
1. **测试方式**：必须通过调用终端命令的方式执行测试流程
2. **测试命令**：使用标准Go测试命令
   ```bash
   # 运行所有测试
   go test ./...
   
   # 运行特定包的测试
   go test ./check
   ```
3. **禁止直接运行**：不得直接运行工作区中的编译文件，必须使用指定目录中的可执行文件

---

## 开发指南

### 代码结构

1. **检测流程** (`check/check.go`):
   - 阶段一：测活 (TCP 检测)
   - 阶段二：测速 (下载测速)
   - 阶段三：媒体解锁检测 (Netflix, YouTube, OpenAI, GPT, TikTok 等)

2. **代理处理** (`proxy/`):
   - 订阅获取与解析
   - 节点去重
   - IP 地理位置查询
   - 节点重命名

3. **Web 服务** (`app/server.go`):
   - 订阅转换 API
   - WebUI 管理界面
   - Sub-store 服务

### 关键配置文件

- `config/config.yaml` - 主配置文件
- `config/config.yaml.example` - 配置示例（最新功能参考）

### 常用开发命令

```bash
# 代码格式化
go fmt ./...

# 代码检查
go vet ./...

# 依赖整理
go mod tidy

# 运行测试
go test ./...

# 生成 Windows 资源文件
go generate ./...
```

---

## 主要模块说明

### check 模块

负责代理节点的核心检测逻辑：

- `check.go` - 检测主流程、并发控制
- `progress.go` - 进度跟踪
- `decay.go` - 成功节点衰减算法

### platform 子模块

各平台媒体解锁检测：

| 文件 | 检测内容 |
|------|----------|
| `netflix.go` | Netflix 解锁 |
| `youtube.go` | YouTube Premium |
| `openai.go` | OpenAI (ChatGPT) |
| `gemini.go` | Google Gemini |
| `tiktok.go` | TikTok 区域 |
| `disney.go` | Disney+ |
| `google.go` | Google 服务 |
| `cloudflare.go` | Cloudflare CDN |
| `iprisk.go` | IP 风险检测 |
| `speed.go` | 速度测试 |

### proxy 模块

- `info.go` - 获取节点地理位置和增强标签
- `get.go` - 订阅链接获取和解析
- `dedup.go` - 节点去重
- `rename.go` - 节点重命名

### save 模块

支持多种保存方式：

- `local` - 本地文件
- `r2` - Cloudflare R2
- `gist` - GitHub Gist
- `webdav` - WebDAV
- `s3` - S3/MinIO

---

## 测试相关

项目中包含部分测试文件：

- `check/decay_test.go` - 衰减算法测试
- `proxy/info_test.go` - 代理信息测试
- `proxy/isp_test.go` - ISP 类型测试
- `proxy/utils_test.go` - 工具函数测试
- `save/method/minio_test.go` - MinIO 测试
- `utils/notify_test.go` - 通知测试
- `utils/proxy_test.go` - 代理工具测试

---

## 注意事项

1. **Windows 构建**: 需要先执行 `go generate ./...` 生成资源文件
2. **Linux/ARM**: sub-store 在 Linux 32 位系统上不支持
3. **Docker**: 自动检测 Docker 环境，禁用自动更新
4. **代理设置**: 支持 system-proxy、github-proxy、ghproxy-group 多级代理
5. **配置更新**: 配置文件修改后会自动监听，热加载需重启生效的部分功能

---

## 相关链接

- 项目地址: https://github.com/sinspired/subs-check-pro
- Docker 镜像: `ghcr.io/sinspired/subs-check-pro:latest`
- Wiki 文档: https://github.com/sinspired/subs-check-pro/wiki
- Telegram 群组: https://t.me/subs_check_pro
