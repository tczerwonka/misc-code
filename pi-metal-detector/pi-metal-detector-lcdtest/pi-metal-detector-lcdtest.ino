// Induction balance metal detector

// We run the CPU at 16MHz and the ADC clock at 1MHz. ADC resolution is reduced to 8 bits at this speed.

// Timer 1 is used to divide the system clock by about 256 to produce a 62.5kHz square wave.
// This is used to drive timer 0 and also to trigger ADC conversions.
// Timer 0 is used to divide the output of timer 1 by 8, giving a 7.8125kHz signal for driving the transmit coil.
// This gives us 16 ADC clock cycles for each ADC conversion (it actually takes 13.5 cycles), and we take 8 samples per cycle of the coil drive voltage.
// The ADC implements four phase-sensitive detectors at 45 degree intervals. Using 4 instead of just 2 allows us to cancel the third harmonic of the
// coil frequency.

// Timer 2 will be used to generate a tone for the earpiece or headset.

// Other division ratios for timer 1 are possible, from about 235 upwards.

// Wiring:
// Connect digital pin 4 (alias T0) to digital pin 9
// Connect digital pin 5 through resistor to primary coil and tuning capacitor
// Connect output from receive amplifier to analog pin 0. Output of receive amplifier should be biased to about half of the analog reference.
// When using USB power, change analog reference to the 3.3V pin, because there is too much noise on the +5V rail to get good sensitivity.
#include <LiquidCrystal.h>
#include <LcdBarGraph.h>
#define max_ampAverage 200
LiquidCrystal lcd(9, 8, 7, 6, 5, 4);

//LiquidCrystal(rs, enable, d4, d5, d6, d7)


LcdBarGraph lbg(&lcd, 16, 0, 1);





void setup()
{
  lcd.begin(16, 2);// LCD 16X2
  
  Serial.begin(19200);

  //test
  lcd.setCursor(0, 0);
  lcd.print("test...  ");
  delay(1000);
  Serial.println("test-setyp");
}



void loop()
{
    Serial.println("test");
  delay(1000);
}
