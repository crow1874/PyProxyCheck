# 🚀 PyProxyCheck - 开源高性能 IP 优选检测系统

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/Framework-FastAPI-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-orange?style=flat-square)
[![Telegram](https://img.shields.io/badge/Telegram-Join%20Group-blue?logo=telegram&style=flat-square)](https://t.me/cfwuya1)

**PyProxyCheck** 是一个基于 **Python 3.10 + FastAPI + Gunicorn** 异步架构构建的高性能代理 IP 检测系统。
本项目内置独家自研的**多重智能验证算法**，能够精准剔除各类**假墙 IP**、**阉割版代理**以及**全通型蜜罐节点**，确保输出的每一个优选 IP 都是真实可用的。

---

## ✨ 核心功能

* **⚡ 极致性能**：底层采用 `uvloop` 异步架构，单机轻松支撑万级并发检测。
* **🛡️ 智能风控**：多维度深度验证，自动识别虚假节点，不仅看 Ping，更看真实可用性。
* **⚙️ 自动优化**：安装脚本自动开启 BBR 加速、解除系统连接数限制。
* **📱 完美 UI**：磨砂玻璃设计风格，PC/手机自适应，自动同步 Bing 每日壁纸。

---

## 💬 交流与反馈

*   **Telegram 频道**: [https://t.me/cfwuya1](https://t.me/cfwuya1)
*   **项目地址**: [https://github.com/crow1874/PyProxyCheck](https://github.com/crow1874/PyProxyCheck)

---

## 🚀 VPS 一键全自动部署

我们提供了极其强大的安装脚本，支持 **基础版** 和 **独立域名版** 两种模式。

### 部署方法

1.  **登录 VPS** (使用 SSH 连接)。
2.  **执行安装命令**：
    ```bash
    wget -O install.sh https://raw.githubusercontent.com/crow1874/PyProxyCheck/main/install.sh && chmod +x install.sh && ./install.sh
    ```

### 🛠️ 安装过程中的模式选择

脚本运行后，会出现以下菜单供您选择：

#### 1️⃣ 模式一：基础极速版 (推荐配合 Cloudflare)
* **适用场景**：您已有域名托管在 Cloudflare，想利用 CF 的 CDN 进行防护。
* **功能**：仅部署后端服务，开放 `8000` 端口。
* **后续操作**：在 Cloudflare 后台添加 A 记录指向 VPS IP，并开启小黄云（Proxy）。

#### 2️⃣ 模式二：独立域名版 (自动 SSL)
* **适用场景**：您希望 VPS 直接提供 HTTPS 服务，不需要 Cloudflare 或其他 CDN。
* **功能**：
    * 自动安装 Nginx。
    * **自动申请 Let's Encrypt 证书**。
    * 自动配置反向代理和证书续期。
* **要求**：执行脚本前，请务必先将您的域名解析（A记录）到这台 VPS 的 IP。

---

## ⚙️ 进阶配置：Cloudflare 设置指南

如果您选择了 **模式一** 并开启了 Cloudflare 小黄云，为防止高并发检测被误拦截，请**务必**进行以下设置：

1.  **SSL/TLS 模式**：
    * 设置为 **完全 (严格) / Full (Strict)**。

2.  **关闭页面缓存 (Page Rules)**：
    * **URL**: `您的域名/*`
    * **设置**: 缓存级别 (Cache Level) -> **绕过 (Bypass)**。

3.  **WAF 白名单 (安全性 -> WAF -> 自定义规则)**：
    * **创建规则**: 主机名 (Hostname) 等于 `您的域名`。
    * **采取措施**: **跳过 (Skip)**。
    * **必须勾选跳过以下组件**：
        * ✅ 所有速率限制规则
        * ✅ 所有超级机器人模式
        * ✅ 浏览器完整性检查 (Browser Integrity Check)
        * ✅ 用户代理阻止 (User Agent Blocking)

---

## 📊 API 接口文档

本项目对外开放 RESTful API，方便集成到其他工具中。

**接口地址**: `https://您的域名/ip={目标IP:端口}`
**请求方式**: `GET`

**返回示例**:
```json
[
  {
    "状态": "有效的 Proxyip",
    "地址": "1.1.1.1:443",
    "地区": "美国",
    "原始输入": "1.1.1.1:443"
  }
]
