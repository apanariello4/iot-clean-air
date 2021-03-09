
const int analogInPin = A0;
int sensorValuePM10 = 0;


void setup() {

  Serial.begin(9600);

}

void loop() {

  sensorValuePM10 = analogRead(analogInPin);

  Serial.write(0xff);
  Serial.write(0x01);
  Serial.write((char)(map(sensorValuePM10,0,1024,0,253)));
  Serial.write(0xfe);

  delay(1000);
}
