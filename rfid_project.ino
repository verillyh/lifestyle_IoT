#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 53
#define RST_PIN 5
#define BUZZER_PIN 7

MFRC522 rfid(SS_PIN, RST_PIN);
byte authorizedUID1[] = {0x43, 0x70, 0x5E, 0xF5};
int unauthorizedAttempts = 0;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  Serial.println("=================================");
  Serial.println(" Welcome to Vinny's Smart Room 🔐");
  Serial.println("=================================");
  Serial.println("Scan your RFID tag...");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  String scannedUID = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) scannedUID += "0";
    scannedUID += String(rfid.uid.uidByte[i], HEX);
  }
  scannedUID.toUpperCase();

  Serial.println("Scanned UID: " + scannedUID);

  if (isAuthorized(rfid.uid.uidByte)) {
    Serial.println("ACCESS GRANTED");
    unauthorizedAttempts = 0;
    delay(10000);
    Serial.println("Auto-locking...");
  } else {
    Serial.println("NO ACCESS");
    unauthorizedAttempts++;
    if (unauthorizedAttempts >= 3) {
      Serial.println("⚠️  Intruder alert! 🚨");
      Serial.println("ALARM TRIGGERED");
      digitalWrite(BUZZER_PIN, HIGH);
      delay(5000);
      digitalWrite(BUZZER_PIN, LOW);
      unauthorizedAttempts = 0;
    }
  }

  rfid.PICC_HaltA();
  delay(2000);
  Serial.println("Scan your RFID tag...");
}

bool isAuthorized(byte *uid) {
  for (byte i = 0; i < 4; i++) {
    if (uid[i] != authorizedUID1[i]) return false;
  }
  return true;
}


