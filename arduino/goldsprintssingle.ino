const int hallPin = 8;
int hall,old_hall;

void setup() {
  Serial.begin(115200);
  pinMode(hallPin, INPUT);
 
  digitalWrite(hallPin, HIGH);
  pinMode(13, OUTPUT);
}

void loop() {
  hall = digitalRead(hallPin);
  if (hall!=old_hall && hall==LOW) {
    digitalWrite(13,HIGH);
    Serial.write('1');
  } else digitalWrite(13,LOW);
  old_hall=hall;
}

