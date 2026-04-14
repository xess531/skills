#!/usr/bin/env bash
# WuLab Router Impersonator - 一键烧录脚本
# 用法: bash flash.sh [工作目录]
# 全自动：环境搭建 → 检测端口 → 生成代码 → 编译 → 上传 → 扫描验证

set -euo pipefail

FQBN="esp32:esp32:esp32c3"
ESP32_URL="https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json"
SKETCH_NAME="esp32-wifi-connect"
WORK_DIR="${1:-.}"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
info() { echo -e "📦 $1"; }

# ========== 1. 环境 ==========
info "检查开发环境..."

if ! command -v brew &>/dev/null; then
    warn "安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    [[ -f /opt/homebrew/bin/brew ]] && eval "$(/opt/homebrew/bin/brew shellenv)"
fi
ok "Homebrew: $(brew --version 2>/dev/null | head -1)"

if ! command -v arduino-cli &>/dev/null; then
    info "安装 arduino-cli..."
    brew install arduino-cli
fi
ok "arduino-cli: $(arduino-cli version 2>/dev/null | head -1)"

if ! arduino-cli core list 2>/dev/null | grep -q "esp32:esp32"; then
    info "安装 ESP32 核心（需要几分钟）..."
    arduino-cli config init --overwrite 2>/dev/null || true
    arduino-cli config add board_manager.additional_urls "$ESP32_URL"
    arduino-cli core update-index
    arduino-cli core install esp32:esp32
fi
ok "ESP32 核心已就绪"

# ========== 2. 检测端口 ==========
PORT=$(ls /dev/cu.usbmodem* 2>/dev/null | head -1 || true)
if [[ -z "$PORT" ]]; then
    err "未检测到 ESP32-C3，请插入 USB 后重新运行"
    exit 1
fi
ok "端口: $PORT"

# ========== 3. 生成固件 ==========
SKETCH_DIR="$WORK_DIR/$SKETCH_NAME"
mkdir -p "$SKETCH_DIR"

cat > "$SKETCH_DIR/$SKETCH_NAME.ino" << 'FIRMWARE'
#include <WiFi.h>
#include "esp_wifi.h"

const char* AP_SSID = "HUAWEI-wulab";
const char* AP_PASSWORD = "12345678";
const int AP_CHANNEL = 1;
uint8_t TARGET_BSSID[] = {0xA2, 0xA9, 0x9A, 0x9C, 0xE6, 0xE6};

unsigned long lastPrint = 0;

void setup() {
    Serial.begin(115200);
    delay(3000);
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASSWORD, AP_CHANNEL, 0, 4);
    delay(1000);
    esp_wifi_set_mac(WIFI_IF_AP, TARGET_BSSID);
    delay(200);

    uint8_t mac[6];
    esp_wifi_get_mac(WIFI_IF_AP, mac);
    Serial.println("=== WuLab Router Impersonator ===");
    Serial.printf("SSID:   %s\n", AP_SSID);
    Serial.printf("CH:     %d\n", AP_CHANNEL);
    Serial.printf("BSSID:  %02X:%02X:%02X:%02X:%02X:%02X\n",
        mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    Serial.printf("IP:     %s\n", WiFi.softAPIP().toString().c_str());
    Serial.println("=================================");
}

void loop() {
    if (millis() - lastPrint >= 5000) {
        lastPrint = millis();
        Serial.printf("[%lus] AP online | clients: %d\n",
            millis() / 1000, WiFi.softAPgetStationNum());
    }
}
FIRMWARE

ok "固件代码已生成"

# ========== 4. 编译上传 ==========
info "编译中..."
arduino-cli compile --fqbn "$FQBN" "$SKETCH_DIR"
ok "编译完成"

info "上传到 $PORT ..."
arduino-cli upload --fqbn "$FQBN" --port "$PORT" "$SKETCH_DIR"
ok "上传完成"

# ========== 5. 扫描验证 ==========
info "等待 AP 启动（8秒）..."
sleep 8

swift - << 'SCANEOF'
import CoreWLAN
let c = CWWiFiClient.shared()
guard let i = c.interface() else { print("❌ 无 WiFi 接口"); exit(1) }
do {
    let nets = try i.scanForNetworks(withName: nil)
    let hw = nets.filter { ($0.ssid ?? "").contains("HUAWEI-wulab") }
    if hw.isEmpty {
        print("⚠️  未扫描到 HUAWEI-wulab（2.4GHz），可用手机确认")
    } else {
        print("✅ 扫描结果:")
        for n in hw.sorted(by: { $0.rssiValue > $1.rssiValue }) {
            let ch = n.wlanChannel?.channelNumber ?? 0
            let band = ch > 14 ? "5GHz" : "2.4GHz"
            print("  HUAWEI-wulab  \(n.rssiValue)dBm  CH:\(ch) (\(band))")
        }
    }
} catch { print("扫描失败: \(error)") }
SCANEOF

echo ""
ok "烧录完成！拔下这块，插入下一块再次运行即可。"
