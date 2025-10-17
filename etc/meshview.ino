// Example to receive and decode Meshtastic UDP packets
// Make sure to install the meashtastic library and generate the .pb.h and .pb.c files from the Meshtastic .proto definitions
// https://github.com/meshtastic/protobufs/tree/master/meshtastic

// Example to receive and decode Meshtastic UDP packets

#include <WiFi.h>
#include <WiFiUdp.h>
// #include <AESLib.h> // or another AES library

#include "pb_decode.h"
#include "meshtastic/mesh.pb.h"      // MeshPacket, Position, etc.
#include "meshtastic/portnums.pb.h"  // Port numbers enum
#include "meshtastic/telemetry.pb.h" // Telemetry message

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

const char* default_key = "1PG7OiApB1nwvP+rz05pAQ=="; // Your network key here
uint8_t aes_key[16]; // Buffer for decoded key

const char* MCAST_GRP = "224.0.0.69";
const uint16_t MCAST_PORT = 4403;

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
  const unsigned long wifiTimeout = 20000;

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
    Serial.println("Check SSID, range, and password.");
  }
}

void printHex(const uint8_t* buf, size_t len) {
  for (size_t i = 0; i < len; i++) {
    Serial.printf("%02X ", buf[i]);
  }
  Serial.println();
}

void printAscii(const uint8_t* buf, size_t len) {
  for (size_t i = 0; i < len; i++) {
    char c = static_cast<char>(buf[i]);
    Serial.print(isprint(c) ? c : '.');
  }
  Serial.println();
}

void decodeKey() {
  // Convert base64 key to raw bytes
  // You may need to add a base64 decoding function/library
  // Example: decode_base64(default_key, aes_key, sizeof(aes_key));
}

void decryptPayload(const uint8_t* encrypted, size_t len, uint8_t* decrypted) {
  // Use AESLib or similar to decrypt
  // Example: aes128_dec_single(decrypted, encrypted, aes_key);
}

void loop() {
  int packetSize = udp.parsePacket();
  if (!packetSize) {
    delay(50);
    return;
  }

  udpPacketCount++;
  Serial.print("UDP packets seen: ");
  Serial.println(udpPacketCount);

  uint8_t buffer[512];
  int len = udp.read(buffer, sizeof(buffer));
  if (len <= 0) {
    Serial.println("Failed to read UDP packet.");
    delay(50);
    return;
  }

  // Always show raw payload
  Serial.print("Raw UDP payload (hex): ");
  printHex(buffer, len);
  Serial.print("Raw UDP payload (ASCII): ");
  printAscii(buffer, len);

  // Decode outer MeshPacket
  meshtastic_MeshPacket pkt = meshtastic_MeshPacket_init_zero;
  pb_istream_t stream = pb_istream_from_buffer(buffer, len);

  if (!pb_decode(&stream, meshtastic_MeshPacket_fields, &pkt)) {
    Serial.println("Failed to decode meshtastic_MeshPacket.");
    delay(50);
    return;
  }

  // Basic MeshPacket fields
  Serial.print("id: "); Serial.println(pkt.id);
  Serial.print("rx_time: "); Serial.println(pkt.rx_time);
  Serial.print("rx_snr: "); Serial.println(pkt.rx_snr, 2);
  Serial.print("rx_rssi: "); Serial.println(pkt.rx_rssi);
  Serial.print("hop_limit: "); Serial.println(pkt.hop_limit);
  Serial.print("priority: "); Serial.println(pkt.priority);
  Serial.print("from: "); Serial.println(pkt.from);
  Serial.print("to: "); Serial.println(pkt.to);
  Serial.print("channel: "); Serial.println(pkt.channel);

  // Only proceed if we have a decoded Data variant
  if (pkt.which_payload_variant != meshtastic_MeshPacket_decoded_tag) {
    Serial.println("Packet does not contain decoded Data (maybe encrypted or other variant).");
    delay(50);
    return;
  }

  const meshtastic_Data& data = pkt.decoded;
  Serial.print("Portnum: "); Serial.println(data.portnum);
  Serial.print("Payload size: "); Serial.println(data.payload.size);

  if (data.payload.size == 0) {
    Serial.println("No inner payload bytes.");
    delay(50);
    return;
  }

  // Decode by portnum
  switch (data.portnum) {

    case meshtastic_PortNum_TEXT_MESSAGE_APP: {
      // Current schemas do not use a separate user.pb.h. Text payload is plain bytes.
      Serial.print("Decoded text message: ");
      printAscii(data.payload.bytes, data.payload.size);
      break;
    }

    case meshtastic_PortNum_POSITION_APP: {
      meshtastic_Position pos = meshtastic_Position_init_zero;
      pb_istream_t ps = pb_istream_from_buffer(data.payload.bytes, data.payload.size);
      if (pb_decode(&ps, meshtastic_Position_fields, &pos)) {
        Serial.print("Position lat="); Serial.print(pos.latitude_i / 1e7, 7);
        Serial.print(" lon="); Serial.print(pos.longitude_i / 1e7, 7);
        Serial.print(" alt="); Serial.println(pos.altitude);
      } else {
        Serial.println("Failed to decode Position payload.");
      }
      break;
    }

    case meshtastic_PortNum_TELEMETRY_APP: {
      meshtastic_Telemetry tel = meshtastic_Telemetry_init_zero;
      pb_istream_t ts = pb_istream_from_buffer(data.payload.bytes, data.payload.size);
      if (pb_decode(&ts, meshtastic_Telemetry_fields, &tel)) {
        // Print a few common fields if present
        if (tel.which_variant == meshtastic_Telemetry_device_metrics_tag) {
          const meshtastic_DeviceMetrics& m = tel.variant.device_metrics;
          Serial.print("Telemetry battery_level="); Serial.print(m.battery_level);
          Serial.print(" voltage="); Serial.print(m.voltage);
          Serial.print(" air_util_tx="); Serial.println(m.air_util_tx);
        } else {
          Serial.println("Telemetry decoded, different variant. Raw bytes:");
          printHex(data.payload.bytes, data.payload.size);
        }
      } else {
        Serial.println("Failed to decode Telemetry payload.");
      }
      break;
    }

    default: {
      Serial.print("Unhandled portnum "); Serial.print((int)data.portnum);
      Serial.println(", showing payload as hex:");
      printHex(data.payload.bytes, data.payload.size);
      break;
    }
  }

  delay(50);
}
