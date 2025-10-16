// Example to receive and decode Meshtastic UDP packets
// Make sure to install the meashtastic library and generate the .pb.h and .pb.c files from the Meshtastic .proto definitions
// https://github.com/meshtastic/protobufs/tree/master/meshtastic
// https://github.com/meshtastic/Meshtastic-arduino/tree/master/src

#include <WiFi.h>
#include <WiFiUdp.h>
#include "mesh.pb.h"
#include "pb_decode.h"
#include <ctype.h>
#include <string.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

const char* MCAST_GRP = "224.0.0.69";
const uint16_t MCAST_PORT = 4403;
const char* PUBKEY = "1PG7OiApB1nwvP+rz05pAQ==";

unsigned long udpPacketCount = 0;

WiFiUDP udp;
IPAddress multicastIP;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Scanning for WiFi networks...");
  int n = WiFi.scanNetworks();
  if (n == 0) {
    Serial.println("No networks found.");
  } else {
    Serial.print(n);
    Serial.println(" networks found:");
    for (int i = 0; i < n; ++i) {
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (RSSI ");
      Serial.print(WiFi.RSSI(i));
      Serial.print(")");
      Serial.println((WiFi.encryptionType(i) == WIFI_AUTH_OPEN) ? " [OPEN]" : " [SECURED]");
      delay(10);
    }
  }
  Serial.println("Connecting to WiFi...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  unsigned long startAttemptTime = millis();
  const unsigned long wifiTimeout = 20000; // 20 seconds

  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < wifiTimeout) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected.");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());

    multicastIP.fromString(MCAST_GRP);
    if (udp.beginMulticast(multicastIP, MCAST_PORT)) {
      Serial.println("UDP multicast listener started.");
    } else {
      Serial.println("Failed to start UDP multicast listener.");
    }

  } else {
    Serial.print("\nFailed to connect to WiFi. SSID: ");
    Serial.println(ssid);
    Serial.println("Check if the SSID is correct and in range, and verify your password.");
  }
}

// Base64 decode helper (returns number of output bytes)
static size_t b64_decode(const char *in, uint8_t *out) {
  size_t len = strlen(in);
  int val = 0, valb = -8;
  size_t o = 0;
  for (size_t i = 0; i < len; ++i) {
    unsigned char c = in[i];
    int d;
    if (c >= 'A' && c <= 'Z') d = c - 'A';
    else if (c >= 'a' && c <= 'z') d = c - 'a' + 26;
    else if (c >= '0' && c <= '9') d = c - '0' + 52;
    else if (c == '+') d = 62;
    else if (c == '/') d = 63;
    else if (c == '=') break;
    else continue;
    val = (val << 6) + d;
    valb += 6;
    if (valb >= 0) {
      out[o++] = (uint8_t)((val >> valb) & 0xFF);
      valb -= 8;
    }
  }
  return o;
}

// Buisness happens here
void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    udpPacketCount++; // Increment counter
    Serial.print("UDP packets seen: ");
    Serial.println(udpPacketCount);

    uint8_t buffer[512];
    int len = udp.read(buffer, sizeof(buffer));
    if (len <= 0) {
      //Serial.println("Failed to read UDP packet.");
      delay(100);
      return;
    }

    meshtastic_MeshPacket packet = meshtastic_MeshPacket_init_zero;
    pb_istream_t stream = pb_istream_from_buffer(buffer, len);

    if (!pb_decode(&stream, meshtastic_MeshPacket_fields, &packet)) {
      Serial.print("Failed to decode Meshtastic_MeshPacket: ");
      Serial.println(PB_GET_ERROR(&stream));
      // print raw packet ASCII
      Serial.println("Raw packet as ASCII:");
      for (int i = 0; i < len; i++) {
        char c = buffer[i];
        if (isprint((unsigned char)c)) Serial.print(c);
        else Serial.print('.');
      }
      Serial.println();
      delay(100);
      return;
    }

    // Print header/meta
    Serial.print("id: "); Serial.println(packet.id);
    Serial.print("rx_time: "); Serial.println(packet.rx_time);
    Serial.print("rx_snr: "); Serial.println(packet.rx_snr, 2);
    Serial.print("hop_limit: "); Serial.println(packet.hop_limit);
    Serial.print("priority: "); Serial.println(packet.priority);
    Serial.print("rx_rssi: "); Serial.println(packet.rx_rssi);
    Serial.print("hop_start: "); Serial.println(packet.hop_start);
    Serial.print("delayed: "); Serial.println(packet.delayed);
    Serial.print("via_mqtt: "); Serial.println(packet.via_mqtt);
    Serial.print("from: "); Serial.println(packet.from);
    Serial.print("to: "); Serial.println(packet.to);
    Serial.print("channel: "); Serial.println(packet.channel);

    // Decode PUBKEY base64 and provide to packet.key
    uint8_t keybin[64];
    size_t keylen = b64_decode(PUBKEY, keybin);
    if (keylen == 0) {
      Serial.println("Warning: PUBKEY base64 decode produced 0 bytes; using raw string bytes");
      static uint8_t saved_key_raw[64];
      size_t rawlen = strlen(PUBKEY);
      if (rawlen > sizeof(saved_key_raw)) rawlen = sizeof(saved_key_raw);
      memcpy(saved_key_raw, PUBKEY, rawlen);
      packet.key.bytes = saved_key_raw;
      packet.key.size = rawlen;
    } else {
      static uint8_t saved_key[64];
      if (keylen > sizeof(saved_key)) keylen = sizeof(saved_key);
      memcpy(saved_key, keybin, keylen);
      packet.key.bytes = saved_key;
      packet.key.size = keylen;
    }

    // Always attempt to process decoded payload
    Serial.println("Attempting to process decoded payload...");
    meshtastic_Data data = packet.decoded; // try to read decoded variant

    Serial.print("Data portnum: "); Serial.println(data.portnum);
    Serial.print("Data payload size: "); Serial.println(data.payload.size);

    if (data.payload.size > 0 && data.payload.bytes != NULL) {
      // Print payload as hex
      Serial.print("Data payload (hex): ");
      for (size_t i = 0; i < data.payload.size; i++) {
        Serial.printf("%02X ", data.payload.bytes[i]);
      }
      Serial.println();

      // Print payload as ASCII with non-printables as '.'
      Serial.print("Data payload (string): ");
      for (size_t i = 0; i < data.payload.size; i++) {
        char c = data.payload.bytes[i];
        if (isprint((unsigned char)c)) Serial.print(c);
        else Serial.print('.');
      }
      Serial.println();
    } else {
      Serial.println("No decoded payload. Raw packet as ASCII:");
      for (int i = 0; i < len; i++) {
        char c = buffer[i];
        if (isprint((unsigned char)c)) Serial.print(c);
        else Serial.print('.');
      }
      Serial.println();
    }
  }

  delay(100); // Small delay to avoid overwhelming the serial output
}