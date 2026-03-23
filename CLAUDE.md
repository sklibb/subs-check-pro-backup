# CLAUDE.md

本文件为 Claude Code 在本仓库中工作时提供指导。

## 架构概述

### 高层设计

**Subs-Check PRO** 是一个高性能代理订阅检测工具，构建为 Go Web 应用程序。其架构采用模块化设计：

```
┌─────────────────────────────────────────────────────────────┐
│                    Web 服务器层 (Gin)                          │
│  ┌──────────┬──────────┬──────────┬──────────┬────────────┐  │
│  │ Admin    │ Analysis │ Share    │ Files    │ API        │  │
│  │ Panel    │ Report   │ Routes   │ Service  │ Endpoints  │  │
│  └──────────┴──────────┴──────────┴──────────┴────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    核心业务逻辑                                │
│  ┌──────────┬──────────┬──────────┬────────────────────────┐ │
│  │ Check    │ Analysis │ Save     │ Config Management       │ │
│  │ Engine   │ Stats    │ Methods  │                        │ │
│  └──────────┴──────────┴──────────┴────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    数据与资源层                                │
│  配置文件 | 模板 | 静态资源 | 输出目录                         │
└─────────────────────────────────────────────────────────────┘
```

### 关键组件

1. **app/server.go** - HTTP 服务器初始化、路由设置、中间件配置
2. **check/** - 核心代理检测逻辑（速度测试、可用性检测）
3. **config/** - 使用 YAML 解析和验证的配置管理
4. **save/method/** - 不同输出方法的实现
5. **assets/** - 嵌入的静态文件和模板
6. **utils/** - 各种实用函数

### 数据流

```
用户请求 → Gin 路由器 → 处理器 → 检测引擎 → 结果 → 输出/分享
                    ↓
              配置加载
                    ↓
              模板渲染
```

## 常用开发命令

### 构建项目

```bash
# 为当前平台构建
GOOS=$(go env GOOS) GOARCH=$(go env GOARCH) go build -o subs-check-pro.exe ./cmd/subs-check-pro

# 跨平台编译为 Windows
GOOS=windows GOARCH=amd64 go build -o subs-check-pro.exe ./cmd/subs-check-pro

# 使用竞态检测构建（调试用）
go build -race -o subs-check-pro.exe ./cmd/subs-check-pro
```

### 本地运行

```bash
# 调试模式，详细日志
gotestsum -- -v -count=1 ./...

# 运行单个测试文件
go test -v ./check/

# 使用覆盖率运行测试
GOFLAGS="-cover" go test -coverprofile=coverage.out ./...
```

### 测试

```bash
# 运行所有测试
go test ./...

# 使用详细输出和竞态检测运行测试
go test -race -v ./...

# 运行特定包的测试
go test -v ./check/

# 生成覆盖率报告
go test -coverprofile=coverage.out ./... && go tool cover -html=coverage.out
```

### 代码质量检查

```bash
# 检查常见问题
go vet ./...

# 格式化代码（提交前）
go fmt ./...

# 使用 golangci-lint 进行代码检查（如果可用）
golangci-lint run
```

## 重要模式和约定

### 配置加载

应用程序采用分层配置方式：
1. `config/config.yaml.example` 中的默认值
2. 环境变量覆盖默认值
3. CLI 参数提供最终覆盖
4. 开发时通过文件监听器热重载

关键配置结构：
```go
type GlobalConfig struct {
    EnableWebUI     bool
    ListenPort      string
    APIKey          string
    SubStorePath    string
    // ... 更多字段
}
```

### 模板系统

- 使用 `embed` 指令嵌入模板以实现高效加载
- 模式：`templates/*.html`
- 管理面板使用 Go 模板，数据通过上下文传递

### 静态资源

- 使用 `assets.StaticFS` 嵌入
- 包含 WebUI 的 CSS、JS、图片
- ACL4SSR 规则等公共文件无需认证即可提供

### API 认证

- 保护路由使用 `X-API-Key` 头进行认证
- 使用 `crypto/subtle.ConstantTimeCompare` 实现防时序攻击的比较
- 如果配置或环境变量中未设置，自动生成默认密钥

## 测试指南

1. **单元测试**位于源代码旁边的 `*_test.go` 文件中
2. 测试使用表格驱动模式以实现全面覆盖
3. 模拟外部依赖项（网络调用、文件系统）
4. 开发时使用 `-race` 标志检测数据竞争
5. 覆盖率报告帮助识别未测试的代码路径

## 关键目录

- `app/` - 主应用程序逻辑和 HTTP 服务器
- `check/` - 代理检测引擎实现
- `config/` - 配置解析和管理
- `save/method/` - 不同输出方法（本地、远程）
- `assets/` - 嵌入的静态文件和模板
- `templates/` - WebUI 的 HTML 模板
- `cmd/subs-check-pro/` - 主入口点

## 环境变量

| 变量 | 说明 |
|----------|-------------|
| `API_KEY` | API 认证密钥（覆盖配置） |
| `HTTP_PROXY` / `HTTPS_PROXY` | 系统代理设置 |
| `SOCKS5_PROXY` | SOCKS5 代理配置 |

## 开发注意事项

1. 应用程序支持在开发时热重载配置文件
2. 静态资源在构建时使用 Go 的 embed 功能嵌入
3. API 路由需要通过 X-API-Key 头进行认证
4. 可以通过设置 `EnableWebUI=false` 并提供 API 密钥来禁用管理面板
5. 输出目录结构会自动创建并设置正确的权限
