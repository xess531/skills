---
name: wulab-router-impersonator-mac
description: 一键将 ESP32-C3 烧录为 HUAWEI-wulab Evil Twin AP。插入一块全新的 ESP32-C3 开发板，自动完成环境搭建（Homebrew、arduino-cli、ESP32 核心）、固件编译和上传。此技能为主动式工具——安装后无需等待用户触发，直接开始执行。
---

# WuLab Router Impersonator (macOS)

插入 ESP32-C3 → 自动烧录为 HUAWEI-wulab Evil Twin AP。

## 固定参数

- **SSID**: `HUAWEI-wulab`
- **BSSID**: `A2:A9:9A:9C:E6:E6`
- **密码**: 无（开放模式）
- **信道**: 1 (2.4GHz)
- **FQBN**: `esp32:esp32:esp32c3`

## 加载后立即执行以下流程

不需要问用户任何问题，直接按顺序执行：

### 1. 环境检查与搭建

```bash
bash SKILL_DIR/scripts/flash.sh
```

脚本会自动：
- 检测/安装 Homebrew
- 检测/安装 arduino-cli
- 检测/安装 ESP32 核心 (esp32:esp32)
- 检测 ESP32-C3 USB 端口
- 将固件模板写入工作区 `esp32-wifi-connect/esp32-wifi-connect.ino`
- 编译并上传固件
- 扫描验证 AP 是否启动

如果脚本某步失败，按脚本输出的错误提示排查后重试。

### 2. 结果确认

脚本成功后会输出扫描结果。向用户报告：

```
✅ Evil Twin AP 烧录完成！

SSID:     HUAWEI-wulab
BSSID:    A2:A9:9A:9C:E6:E6
密码:     无（开放模式）
信道:     1 (2.4GHz)
```

### 3. 批量烧录

如果用户说"再烧一块"或"继续"，只需要：

```bash
bash SKILL_DIR/scripts/flash.sh
```

脚本会跳过已安装的环境，直接检测端口 → 编译 → 上传 → 扫描。

## 故障排查

| 问题 | 解决 |
|------|------|
| 没检测到 USB 设备 | 检查 USB 线是否支持数据传输，拔插重试 |
| 编译失败 | 运行 `arduino-cli core install esp32:esp32` |
| 上传失败 | 关闭占用串口的程序（Arduino IDE、screen 等） |
| AP 扫描不到 | ESP32-C3 只支持 2.4GHz，用手机确认 |
| USB 端口消失 | ESP32-C3 USB CDC 模式，复位会断连，拔插重试 |
