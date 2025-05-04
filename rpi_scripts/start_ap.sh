#!/bin/bash
set -e

echo "[1/4] Disconnecting from default Wi-Fi (if connected)..."
nmcli connection down preconfigured 2>/dev/null || true

echo "[2/4] Enabling offline AP mode..."
nmcli connection up offline-ap

echo "[3/4] Starting hostapd and dnsmasq..."
systemctl start hostapd
systemctl start dnsmasq

echo "[4/4] Starting web server (lighttpd)..."
systemctl start lighttpd

echo "✅ Access Point is now active."
echo "📶 SSID: Pi_AP"
echo "🌐 IP: http://192.168.4.1"

