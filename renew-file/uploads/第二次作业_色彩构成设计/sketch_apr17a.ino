// 流水灯实验，使用Arduino UNO R4 WIFI，引脚1~5接LED
const int ledPins[] = {1, 2, 3, 4, 5};
const int numLeds = 5;

void setup() {
  for (int i = 0; i < numLeds; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW); // 初始所有LED熄灭
  }
}

void loop() {
  for (int i = 0; i < numLeds; i++) {
    digitalWrite(ledPins[i], HIGH); // 点亮当前LED
    delay(200);                     // 保持点亮200ms
    digitalWrite(ledPins[i], LOW);  // 熄灭当前LED
  }
}