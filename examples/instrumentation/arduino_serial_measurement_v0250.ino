// Sustainable Catalyst Lab v0.25.0 serial measurement example
// Emits newline-delimited JSON for an Arduino-compatible board.
void setup() { Serial.begin(115200); }
void loop() {
  int raw = analogRead(A0);
  Serial.print("{\"instrumentId\":\"ARDUINO-1\",\"channel\":\"A0\",\"value\":");
  Serial.print(raw);
  Serial.println(",\"unit\":\"adc_count\"}");
  delay(1000);
}
