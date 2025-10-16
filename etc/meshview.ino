// Example to receive and decode Meshtastic UDP packets
// Make sure to install the meashtastic library and generate the .pb.h and .pb.c files from the Meshtastic .proto definitions
// https://github.com/meshtastic/protobufs/tree/master/meshtastic
// https://github.com/meshtastic/Meshtastic-arduino/tree/master/src

// Example to receive and decode Meshtastic UDP packets

#include <WiFi.h>
#include <WiFiUdp.h>
#include "mesh.pb.h"
#include "portnums.pb.h"
#include "user.pb.h"
#include "position.pb.h"
#include "pb_decode.h"

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

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

// Business happens here
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

  // Always print raw payload first
  Serial.print("Raw UDP payload (hex): ");
  for (int i = 0; i < len; i++) Serial.printf("%02X ", buffer[i]);
  Serial.println();

  Serial.print("Raw UDP payload (ASCII): ");
  for (int i = 0; i < len; i++) {
    char c = buffer[i];
    Serial.print(isprint(c) ? c : '.');
  }
  Serial.println();

  // Decode outer MeshPacket
  meshtastic_MeshPacket packet = meshtastic_MeshPacket_init_zero;
  pb_istream_t stream = pb_istream_from_buffer(buffer, len);

  if (!pb_decode(&stream, meshtastic_MeshPacket_fields, &packet)) {
    Serial.println("Failed to decode meshtastic_MeshPacket.");
    delay(50);
    return;
  }

  // Basic MeshPacket fields
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

  // Only proceed if the oneof contains the decoded Data message
  if (packet.which_payload_variant == meshtastic_MeshPacket_decoded_tag) {
    const meshtastic_Data& data = packet.decoded;

    Serial.print("Data portnum: ");
    Serial.println(data.portnum);
    Serial.print("Data payload size: ");
    Serial.println(data.payload.size);

    if (data.payload.size == 0) {
      Serial.println("No decoded payload bytes present.");
      delay(50);
      return;
    }

    // Decode the embedded payload by portnum
    pb_istream_t payload_stream = pb_istream_from_buffer(data.payload.bytes, data.payload.size);

    switch (data.portnum) {
      case meshtastic_PortNum_TEXT_MESSAGE_APP: {
         // Some generated protobuf headers use a different type/name than expected.
         // Safely print the payload as a UTF-8 string instead of relying on the
         // generated meshtastic_UserMessage type/name.
         size_t n = data.payload.size;
         const size_t BUF_SZ = 256;
         char msgbuf[BUF_SZ];
         if (n >= BUF_SZ) n = BUF_SZ - 1;
         memcpy(msgbuf, data.payload.bytes, n);
         msgbuf[n] = '\0';
         Serial.print("Text payload: ");
         Serial.println(msgbuf);
        break;
      }

      case meshtastic_PortNum_POSITION_APP: {
        meshtastic_Position pos = meshtastic_Position_init_zero;
        if (pb_decode(&payload_stream, meshtastic_Position_fields, &pos)) {
          // Positions are typically scaled integers
          Serial.print("Decoded position: lat=");
          Serial.print(pos.latitude_i / 1e7, 7);
          Serial.print(" lon=");
          Serial.print(pos.longitude_i / 1e7, 7);
          Serial.print(" alt=");
          Serial.println(pos.altitude);
        } else {
          Serial.println("Failed to decode Position payload.");
        }
        break;
      }

      // Add other portnums as needed, for example:
      // case meshtastic_PortNum_TELEMETRY_APP: { ... } break;

      default: {
        Serial.print("Unhandled portnum ");
        Serial.print((int)data.portnum);
        Serial.println(", showing payload as hex:");
        for (size_t i = 0; i < data.payload.size; i++) {
          Serial.printf("%02X ", data.payload.bytes[i]);
        }
        Serial.println();
        break;
      }
    }

  } else {
    Serial.println("MeshPacket does not contain decoded Data. It may be encrypted or a different variant.");
  }

  delay(50);
}
