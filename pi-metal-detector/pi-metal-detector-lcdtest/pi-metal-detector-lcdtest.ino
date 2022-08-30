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
LiquidCrystal lcd(6, 10, 9, 14, 15, 16);

//LiquidCrystal(rs, enable, d4, d5, d6, d7)


LcdBarGraph lbg(&lcd, 16, 0, 1);

#define TIMER1_TOP  (259)        // can adjust this to fine-tune the frequency to get the coil tuned (see above)

#define USE_3V3_AREF  (1)        // set to 1 of running on an Arduino with USB power, 0 for an embedded atmega28p with no 3.3V supply available

// Digital pin definitions
// Digital pin 0 not used, however if we are using the serial port for debugging then it's serial input
const int debugTxPin = 1;        // transmit pin reserved for debugging
const int encoderButtonPin = 2;  // encoder button, also IN0 for waking up from sleep mode
const int earpiecePin = 3;       // earpiece, aka OCR2B for tone generation
const int T0InputPin = 4;
const int coilDrivePin = 5;
const int T0OutputPin = 17;

const int LcdRsPin = 6;
const int LcdEnPin = 10;
const int LcdPowerPin = 8;       // LCD power and backlight enable
const int lcdD4Pin = 9;
const int lcdD5Pin = 14;         // pins 11-13 also used for ICSP
const int LcdD6Pin = 15;
const int LcdD7Pin = 16;



void setup()
{
  lcd.begin(16, 2);// LCD 16X2
  
  Serial.begin(19200);

  //test
  lcd.setCursor(0, 0);
  lcd.print("test...  ");
  Serial.println("test");
}



void loop()
{
  
}
