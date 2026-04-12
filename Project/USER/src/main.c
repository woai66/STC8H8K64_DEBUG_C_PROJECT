#include "headfile.h"

#define KEY_PORT P2
#define KEY_NONE 0xFF

volatile int mymode = 0;
volatile int last_mymode = 0;
volatile int mydistance = 0;
volatile int mysquarelength = 0;
volatile unsigned char distance = 0;
volatile unsigned char length = 0;

static float maxpower = 0;
const unsigned char key_map[4][4] = {{'1', '2', '3', 'A'},
                                     {'4', '5', '6', 'B'},
                                     {'7', '8', '9', 'C'},
                                     {'*', '0', '#', 'D'}};

static void keydelay_ms(unsigned int ms) {
  unsigned int i, j;
  for (i = 0; i < ms; i++) {
    for (j = 0; j < 10; j++)
      ;
  }
}

static unsigned char key_scan(void) {
  unsigned char row, col, key_val;
  unsigned char read_val;

  KEY_PORT = 0xF0;
  if ((KEY_PORT & 0x0F) == 0x0F) {
    return KEY_NONE;
  }

  keydelay_ms(5);
  if ((KEY_PORT & 0x0F) == 0x0F) {
    return KEY_NONE;
  }

  for (row = 0; row < 4; row++) {
    if (row == 0)
      KEY_PORT = ~(0x10);
    if (row == 1)
      KEY_PORT = ~(0x20);
    if (row == 2)
      KEY_PORT = ~(0x40);
    if (row == 3)
      KEY_PORT = ~(0x80);

    read_val = KEY_PORT & 0x0F;
    if (read_val != 0x0F) {
      switch (read_val) {
      case 0x0E:
        col = 0;
        break;
      case 0x0D:
        col = 1;
        break;
      case 0x0B:
        col = 2;
        break;
      case 0x07:
        col = 3;
        break;
      default:
        return KEY_NONE;
      }

      key_val = key_map[row][col];
      while ((KEY_PORT & 0x0F) != 0x0F) {
        keydelay_ms(1);
      }
      return key_val;
    }
  }

  return KEY_NONE;
}

static void apply_key(unsigned char key, int *lcd_clear_num) {
  switch (key) {
  case '1':
    mymode = 1;
    *lcd_clear_num = 20;
    break;
  case '2':
    mymode = 2;
    *lcd_clear_num = 20;
    break;
  case '3':
    mymode = 3;
    *lcd_clear_num = 20;
    break;
  case '4':
    mymode = 4;
    *lcd_clear_num = 20;
    break;
  case '0':
  case '5':
  case '6':
  case '7':
  case '8':
  case '9':
  case 'A':
  case 'B':
  case 'C':
  case 'D':
  case '*':
  case '#':
  default:
    break;
  }
}

static void write_mode_line(char *text_buffer) {
  if (mymode != 0) {
    sprintf(text_buffer, "MODE:%d D:?? L:??", mymode);
  } else if (last_mymode == 1) {
    sprintf(text_buffer, "BASIC D:%d L:%d", mydistance, mysquarelength);
  } else if (last_mymode == 2) {
    sprintf(text_buffer, "MIN   D:%d L:%d", mydistance, mysquarelength);
  } else if (last_mymode == 3) {
    sprintf(text_buffer, "MAX   D:%d L:%d", mydistance, mysquarelength);
  } else if (last_mymode == 4) {
    sprintf(text_buffer, "TILT  D:%d L:%d", mydistance, mysquarelength);
  } else {
    sprintf(text_buffer, "IDLE  D:%d L:%d", mydistance, mysquarelength);
  }
}

static void send_mode_command(void) {
  uart_putchar(DEBUG_UART, 0x00);
  uart_putchar(DEBUG_UART, 0xff);
  uart_putchar(DEBUG_UART, mymode);
  uart_putchar(DEBUG_UART, 0x00);
  uart_putchar(DEBUG_UART, 0xfe);
}

void main() {
  char text_buffer[20];
  float current;
  float vol;
  float power;
  int lcd_clear_num = 0;
  unsigned char key = KEY_NONE;
  unsigned int j;

  board_init();
  lcd4002_init();
  ina226_init();
  delay_ms(100);
  lcd4002_backlight(1);
  lcd4002_set_rotation(0);
  lcd4002_clear();

  while (1) {
    current = ina226_get_current();
    current /= 1.11f;
    vol = ina226_get_bus_voltage();
    power = current * vol;

    if (maxpower <= power) {
      maxpower = power;
    }

    lcd_clear_num++;
    if (lcd_clear_num >= 50) {
      lcd4002_clear();
      lcd_clear_num = 0;
    }

    sprintf(text_buffer, "I%.3fA V%.3fV P%.3fW MAX%.3f", current, vol, power,
            maxpower);
    lcd4002_write_string_at_r180(0, 1, text_buffer);

    if (mymode != 0) {
      last_mymode = mymode;
    }

    write_mode_line(text_buffer);
    lcd4002_write_string_at_r180(0, 0, text_buffer);

    for (j = 0; j < 20; j++) {
      delay_ms(2);
      key = key_scan();
      if (key != KEY_NONE) {
        apply_key(key, &lcd_clear_num);
      }
    }

    send_mode_command();
  }
}
