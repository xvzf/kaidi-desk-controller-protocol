void setup() {
  Serial.begin(115200); // Ignored for USB CDC

  Serial1.setRX(13);
  Serial1.setTX(12);
  Serial1.begin(9600);

  Serial2.setRX(5);
  Serial2.setTX(4);
  Serial2.begin(9600);
}


char hexString[5];
char val;
void loop() {
  if (Serial1.available()) {
    val = Serial1.read();
    sprintf(hexString, "0x%02X", val);
    Serial.print("<");
    Serial.println(hexString);
  }
  if (Serial2.available()) {
    val = Serial2.read();
    sprintf(hexString, "0x%02X", val);
    Serial.print(">");
    Serial.println(hexString);
  }

}
