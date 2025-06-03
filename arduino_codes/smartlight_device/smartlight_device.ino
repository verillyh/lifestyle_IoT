const int motionPin = 10;
const int redPin = 5;
const int greenPin = 6;
const int bluePin = 7;

bool previousState = LOW;
String mode = "morning light";
bool overrideOn = false;
bool overrideOff = false;
bool partyModeActive = false;

unsigned long motionStartTime = 0;
bool motionActive = false;

void setup()
{
  pinMode(motionPin, INPUT);
  Serial.begin(9600);

  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  setColor(0, 0, 0);
  Serial.println("Ready - Default mode: MORNING");
}

void loop()
{
  if (Serial.available())
  {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "lights on")
    {
      overrideOn = true;
      overrideOff = false;
      motionActive = false;
      Serial.println("Override: LED ON");
      if (mode == "party light")
      {
        partyModeActive = true;
      }
      else
      {
        applyColorMode();
      }
    }
    else if (command == "lights off")
    {
      overrideOn = false;
      overrideOff = true;
      motionActive = false;
      partyModeActive = false;
      setColor(0, 0, 0);
      Serial.println("Override: LED OFF (total)");
    }
    else if (command == "motion lights")
    {
      overrideOn = false;
      overrideOff = false;
      partyModeActive = (mode == "party light");
      Serial.println("AUTO mode enabled (motion detection resumes)");
    }
    else if (command == "morning light" || command == "afternoon light" || command == "evening light" ||
             command == "night light" || command == "party light" ||
             command == "happy light" || command == "sad light" || command == "relax light" ||
             command == "love light" || command == "angry light" || command == "romantic light")
    {
      mode = command;
      partyModeActive = (mode == "party light");
      Serial.print("Mode set to: ");
      Serial.println(mode);
      if (overrideOn && mode != "party light")
      {
        applyColorMode();
      }
    }
  }

  if (overrideOff)
  {
    setColor(0, 0, 0);
    return;
  }

  if (overrideOn)
  {
    if (partyModeActive)
    {
      partyBlink();
    }
    return;
  }

  if (partyModeActive && motionActive)
  {
    partyBlink();
    return;
  }

  bool currentState = digitalRead(motionPin);

  if (currentState == HIGH && !motionActive)
  {
    motionStartTime = millis();
    motionActive = true;
    Serial.println("Motion Detected");
    if (!partyModeActive)
      applyColorMode();
  }

  if (motionActive && millis() - motionStartTime >= 3000)
  {
    Serial.println("Motion expired, turning off LED");
    motionActive = false;
    setColor(0, 0, 0);
  }

  previousState = currentState;
  delay(100);
}

void applyColorMode()
{
  if (mode == "morning light")
    setColor(255, 223, 186);
  else if (mode == "noon light")
    setColor(180, 220, 255);
  else if (mode == "evening light")
    setColor(255, 140, 0);
  else if (mode == "night light")
    setColor(128, 0, 64);
  else if (mode == "happy light")
    setColor(255, 255, 0);
  else if (mode == "sad light")
    setColor(0, 0, 255);
  else if (mode == "relax light")
    setColor(135, 206, 250);
  else if (mode == "love light")
    setColor(255, 20, 147);
  else if (mode == "angry light")
    setColor(255, 0, 0);
  else if (mode == "romantic light")
    setColor(128, 0, 128);
}

void setColor(int redValue, int greenValue, int blueValue)
{
  analogWrite(redPin, redValue);
  analogWrite(greenPin, greenValue);
  analogWrite(bluePin, blueValue);
}

void partyBlink()
{
  static unsigned long lastBlink = 0;
  static bool ledOn = false;

  if (millis() - lastBlink >= 200)
  {
    lastBlink = millis();
    if (ledOn)
    {
      setColor(0, 0, 0);
    }
    else
    {
      setColor(random(0, 256), random(0, 256), random(0, 256));
    }
    ledOn = !ledOn;
  }
}
