#define PWM_PIN 4
#define RESOLUTION 256
#define FREQUENCY 38000

uint32_t sampleIndex = 0;
#include "driver/adc.h"
String send_str = "";


void setup() {
  Serial.begin(460800);
  pinMode(PWM_PIN, OUTPUT);  // Enable PWM on pin 9

  analogWriteResolution(PWM_PIN, RESOLUTION);
  analogWriteFrequency(PWM_PIN, FREQUENCY);

  adc1_config_width(ADC_WIDTH_BIT_9);                          // 12-bit resolution
  adc1_config_channel_atten(ADC1_CHANNEL_6, ADC_ATTEN_DB_11);  // ~0–3.3V
}


int read_values[10] = { 0 };
uint8_t read_values_pointer = 0;
int maxM = 0;
void loop() {
  analogWriteFrequency(PWM_PIN, FREQUENCY);

  uint8_t str_len = send_str.length();
  if (str_len != 0) {
    for (uint8_t i = 0; i < str_len; i++) {
      uint8_t send_char = send_str.charAt(i);
      Serial.println(send_char);
      for (int8_t j = 7; j >= 0; j--) {
        uint8_t send_bit = bitRead(send_char, j);
        Serial.print(j);
        Serial.print(" - ");
        Serial.println(send_bit);
        uint16_t wait_milis = 0;
        if (send_bit) {
          wait_milis = 10;

        } else {
          wait_milis = 30;
        }
        analogWrite(PWM_PIN, RESOLUTION / 2);
        delay(wait_milis);
        analogWrite(PWM_PIN, 0);
        delay(40 - wait_milis);
      }
    }
    analogWrite(PWM_PIN, RESOLUTION / 2);
    delay(100);
    analogWrite(PWM_PIN, 0);
    send_str = "";
  }
  if (Serial.available()) {
    send_str = Serial.readStringUntil('\n');
  }
}
