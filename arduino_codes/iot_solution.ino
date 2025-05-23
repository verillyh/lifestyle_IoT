#define LED_PIN 13
#define BUZZER_PIN 8
#define PIR_PIN 4
#define MIC_PIN A0

String mode = "STOP";
unsigned long previousBlinkMillis = 0;
unsigned long previousSendMillis = 0;
int ledState = LOW;

void setup()
{
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(MIC_PIN, INPUT);
  Serial.begin(9600);
  Serial.println("Detection System Ready");
}

void loop()
{

  unsigned long currentMillis = millis();

  if (currentMillis - previousSendMillis >= 500)
  {
    previousSendMillis = currentMillis;
    int micValue = analogRead(MIC_PIN);
    bool motionDetected = digitalRead(PIR_PIN) == HIGH;

    Serial.print("MIC:");
    Serial.print(micValue);
    Serial.print(" PIR:");
    Serial.println(motionDetected ? 1 : 0);
  }

  if (Serial.available())
  {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "SLOW" || command == "LOUD" || command == "STOP")
    {
      mode = command;
    }
  }

  if (mode == "SLOW")
  {
    if (currentMillis - previousBlinkMillis >= 800)
    {
      previousBlinkMillis = currentMillis;
      ledState = !ledState;
      digitalWrite(LED_PIN, ledState);
      tone(BUZZER_PIN, 600);
    }
  }
  else if (mode == "LOUD")
  {
    if (currentMillis - previousBlinkMillis >= 150)
    {
      previousBlinkMillis = currentMillis;
      ledState = !ledState;
      digitalWrite(LED_PIN, ledState);
      tone(BUZZER_PIN, 1500);
    }
  }
  else if (mode == "STOP")
  {
    digitalWrite(LED_PIN, LOW);
    noTone(BUZZER_PIN);
  }
}
