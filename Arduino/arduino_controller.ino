/* 

Controls Arduino via serial communication
Dillon Wong 04/08/2018

*/

void setup() {

  DDRD = DDRD | 0xFC;
  DDRB = 0xFF;
  Serial.begin(9600);
}

void loop() {
  
  if (Serial.available()) {
    unsigned char pin_seq = Serial.read();
    int pin_num = 0x0F & pin_seq;
    int pin_state = (0x80 & pin_seq) >> 7;
    int read_state = (0x40 & pin_seq) >> 6;
    if (read_state == 1) {
      if ((pin_num > 1) && (pin_num < 8)) {
        Serial.print(bitRead(PORTD, pin_num));
      }
      else if ((pin_num > 7) && (pin_num < 14)) {
        Serial.print(bitRead(PORTB, pin_num - 8));
      }
    }
    else {
      if (pin_state == 1) {
        digitalWrite(pin_num, HIGH);
      }
      else if (pin_state == 0) {
        digitalWrite(pin_num, LOW);
        }
    }
  }

}
