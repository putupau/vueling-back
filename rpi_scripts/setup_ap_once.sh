#!/bin/bash
set -e

echo "[1/7] Updating system and installing packages..."
apt update
apt install -y hostapd dnsmasq lighttpd qrencode network-manager

systemctl stop hostapd || true
systemctl stop dnsmasq || true

echo "[2/7] Creating dedicated AP profile using NetworkManager..."
nmcli connection delete offline-ap || true
nmcli connection add type wifi ifname wlan0 con-name offline-ap autoconnect no ssid Pi_AP
nmcli connection modify offline-ap mode ap ipv4.method manual ipv4.addresses 192.168.4.1/24
nmcli connection modify offline-ap wifi.band bg wifi.channel 7
nmcli connection modify offline-ap wifi-sec.key-mgmt wpa-psk
nmcli connection modify offline-ap wifi-sec.psk PowerOutage123

echo "[3/7] Configuring dnsmasq..."
mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig 2>/dev/null || true
cat <<EOF > /etc/dnsmasq.conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
address=/#/192.168.4.1
EOF

echo "[4/7] Configuring hostapd..."
cat <<EOF > /etc/hostapd/hostapd.conf
interface=wlan0
driver=nl80211
ssid=Pi_AP
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=PowerOutage123
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
EOF

sed -i 's|^#DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

echo "[5/7] Setting up lighttpd content..."
cat <<EOF > /var/www/html/index.html
<!DOCTYPE html>
<html>
<head><title>Power Outage Detected</title></head>
<body>
  <h1>Emergency Access</h1>
  <p>This page is served from the Raspberry Pi hotspot.</p>
</body>
</html>
EOF

cat <<EOF >> /etc/lighttpd/lighttpd.conf

# Captive portal redirect
$HTTP["host"] =~ "." {
    url.redirect = (".*" => "/index.html")
}
EOF

echo "[6/7] Disabling services on boot (manual activation only)..."
systemctl disable hostapd
systemctl disable dnsmasq
systemctl disable lighttpd

echo "[7/7] Generating QR code for Wi-Fi access..."
qrencode -o /var/www/html/wifi_qr.png "WIFI:S:Pi_AP;T:WPA;P:PowerOutage123;;"

echo "✅ Setup complete. Use the activation script to enable the AP manually."

