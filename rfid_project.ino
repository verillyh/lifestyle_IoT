#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

#define SS_PIN 53
#define RST_PIN 5
#define BUZZER_PIN 7
#define SERVO_PIN 8  // Using pin 8 for servo signal

MFRC522 rfid(SS_PIN, RST_PIN);
Servo lockServo;
String command = "";

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  lockServo.attach(SERVO_PIN);
  lockServo.write(0); // 0° = Locked position

  Serial.println("=================================");
  Serial.println(" Welcome to Vinny's Smart Room 🔐");
  Serial.println("=================================");
  Serial.println("Scan your RFID tag...");
}

void loop() {
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String scannedUID = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      if (rfid.uid.uidByte[i] < 0x10) scannedUID += "0";
      scannedUID += String(rfid.uid.uidByte[i], HEX);
    }
    scannedUID.toUpperCase();

    Serial.println("Scanned UID: " + scannedUID);
    rfid.PICC_HaltA();
    delay(2000);
  }

  if (Serial.available()) {
  command = Serial.readStringUntil('\n');
  command.trim();

  if (command == "ACCESS GRANTED" || command == "UNLOCK") {
    Serial.println("Unlocking door...");
    lockServo.write(90);
    delay(10000);
    lockServo.write(0);
    Serial.println("Auto-locking...");
  } else if (command == "NO ACCESS" || command == "LOCK") {
    Serial.println("Locking door...");
    lockServo.write(0);
  }
  command = "";
  }
}



