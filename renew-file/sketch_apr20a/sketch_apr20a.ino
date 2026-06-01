//这是关于超声波传感器的项目代码
/*
zwu2260420课程测试，此处是用超声波传感器测试计划距离
接线方式是以下
Arduino  SR04
5V    --- VCC
A0    ---Trig
A1    ---Echo
GND   ---GND

参考资料来源于arduino.cc  v0


*/
#define trig A0
#define echo A1
int count = 0;
long duration;
void setup() {
  Serial.begin(115200);
  pinMode (trig,OUTPUT);
  pinMode(echo,INPUT);
  digitalWrite(trig,LOW);
  delay(1);
}
void loop(){
  Serial.println(count++);
  Serial.print(getDistance());
  delay(1000);
  Serial.println("");
  Serial.println("");
}
long getDistance(){
// trig
    digitalWrite(trig, LOW);
    delayMicroseconds(2);
    digitalWrite(trig, HIGH);
    delayMicroseconds(10);
    digitalWrite(trig, LOW);
    // echo
    duration = pulseIn(echo, HIGH); 	// unit: us
    return duration * 0.34029 / 2; 		// unit: mm


}