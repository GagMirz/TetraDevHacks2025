#include <ESP_I2S.h>
#include "driver/adc.h"

uint32_t sum_of_delta = 0;
uint8_t sum_cnt = 0;

void setup() {
  // Initialize serial communication at 115200 bits per second:
  Serial.begin(460800);
  delay(500);

  adc1_config_width(ADC_WIDTH_BIT_9);                          // 12-bit resolution
  adc1_config_channel_atten(ADC1_CHANNEL_6, ADC_ATTEN_DB_11);  // ~0–3.3V
}

bool is_low = true;
uint32_t last_cros_clock = 0;

uint32_t read_values[20] = { 0 };
uint8_t read_values_pointer = 0;

uint8_t bit_addr = 0;
uint8_t rx_byte = 0;


uint32_t last_invers_time = 0;
void loop() {
  int adc_value = adc1_get_raw(ADC1_CHANNEL_6);

  if (adc_value > 300) {
    if (is_low == true) {
      uint32_t delta = (micros() - last_cros_clock);
      if (delta > 200) {
        if (delta > 5000 && delta < 15000) {
          if (bit_addr < 7) {
            rx_byte <<= 1;
          }
          bit_addr++;
        } else if (delta > 15000 && delta < 40000) {
          rx_byte |= 1;
          if (bit_addr < 7) {
            rx_byte <<= 1;
          }
          bit_addr++;
        } else if (delta > 40000) {
          rx_byte = 0;
          bit_addr = 0;
        }

        if (bit_addr == 8) {
          bit_addr = 0;
          Serial.println((char)rx_byte);
          rx_byte = 0;
        }
      }

      last_cros_clock = micros();
      is_low = false;
    }
  } else if (adc_value < 200) {
    if (is_low == false) {
      is_low = true;
    }
  }
}