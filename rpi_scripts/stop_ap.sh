#!/bin/bash
set -e

echo "🔌 Stopping AP and services..."

# Stop services
systemctl stop hostapd || true
systemctl stop dnsmasq || true
systemctl stop lighttpd || true

# Disconnect AP profile
nmcli con down offline-ap || true

# Restart NetworkManager to resume normal networking
systemctl restart NetworkManager

echo "✅ AP and web server stopped. System back to normal network mode."

