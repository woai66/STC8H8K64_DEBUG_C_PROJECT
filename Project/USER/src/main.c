/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2020,��ɿƼ�
 * All rights reserved.
 * ��������QQȺ��һȺ��179029047(����)  ��Ⱥ��244861897(����)  ��Ⱥ��824575535
 *
 * �����������ݰ�Ȩ������ɿƼ����У�δ��������������ҵ��;��
 * ��ӭ��λʹ�ò������������޸�����ʱ���뱣����ɿƼ��İ�Ȩ������
 *
 * @file       		main
 * @company	   		�ɶ���ɿƼ����޹�˾
 * @author     		��ɿƼ�(QQ790875685)
 * @version    		�鿴doc��version�ļ� �汾˵��
 * @Software 		MDK FOR C51 V9.60
 * @Target core		STC8H8K64S4
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2020-06-01
 ********************************************************************************************************************/

#include "headfile.h"

#define KEY_PORT P2
#define KEY_NONE 0xFF   
volatile int mymode=0;
volatile int mydistance=0;
volatile int mysquarelength=0;
volatile unsigned char distance = 0;
volatile unsigned char length = 0;
/*
 * ϵͳƵ�ʣ��ɲ鿴board.h�е� FOSC �궨���޸ġ�
 * board.h�ļ���FOSC��ֵ����Ϊ0,������Զ�����ϵͳƵ��Ϊ44.2368MHZ
 * ��board_init��,�Ѿ���P54��������Ϊ��λ
 * �����Ҫʹ��P54����,������board.c�ļ��е�board_init()������ɾ��SET_P54_RESRT����
 */

/*
 * LCD4002Һ��������˵����
 * ====================================
 * LCD4002ģ�� -----> STC8H8K64��Ƭ��
 * ====================================
 * VCC        -----> 5V (��3.3V������ģ���ѹ)
 * GND        -----> GND
 * SDA        -----> P14 (���I2C������)
 * SCL        -----> P15 (���I2Cʱ����)
 * ====================================
 * 
 * ע�����
 * 1. ȷ��LCD4002ģ���I2C��ַΪ0x27��Ĭ�ϵ�ַ��
 * 2. �����ַ��ͬ�����޸�SEEKFREE_LCD4002_I2C.h�е�LCD4002_I2C_ADDR����
 * 3. �����Ҫ�޸�I2C���ţ����޸�SEEKFREE_SOFT_I2C.h�е����Ŷ���
 */
const unsigned char key_map[4][4] = {
    {'1', '2', '3', 'A'},  
    {'4', '5', '6', 'B'},  
    {'7', '8', '9', 'C'},  
    {'*', '0', '#', 'D'}   
};
void keydelay_ms(unsigned int ms) {
    unsigned int i, j;
    for (i = 0; i < ms; i++) {
        for (j = 0; j < 10; j++);  // ????????
    }
}
unsigned char key_scan() 
{
    static unsigned char last_key = KEY_NONE;
    unsigned char row, col, key_val;
    unsigned char read_val;
    KEY_PORT = 0xF0;  
    if ((KEY_PORT & 0x0F) == 0x0F) {
        last_key = KEY_NONE;
        return KEY_NONE;
    }
    keydelay_ms(5);
    if ((KEY_PORT & 0x0F) == 0x0F) {
        last_key = KEY_NONE;
        return KEY_NONE;
    }
    for (row = 0; row < 4; row++) {
			  if(row == 0)
        KEY_PORT = ~(0x10);  
				if(row == 1)
        KEY_PORT = ~(0x20);  
				if(row == 2)
        KEY_PORT = ~(0x40);  
				if(row == 3)
        KEY_PORT = ~(0x80);  
        read_val = KEY_PORT & 0x0F;
        if (read_val != 0x0F) {
            switch (read_val) {
                case 0x0E: col = 0; break;  // ?0?(P2.0)
                case 0x0D: col = 1; break;  // ?1?(P2.1)
                case 0x0B: col = 2; break;  // ?2?(P2.2)
                case 0x07: col = 3; break;  // ?3?(P2.3)
                default: return KEY_NONE;    // ????,??
            }
            key_val = key_map[row][col];
            while ((KEY_PORT & 0x0F) != 0x0F) {
                keydelay_ms(1);
            }
            if (key_val != last_key) {
                last_key = key_val;
                return key_val;
            }
            return KEY_NONE;
        }
    }
    return KEY_NONE;
}
void main()
{
		char text_buffer[20];
		float current;
		float vol;
		float power;
		float power_get;
	  int lcdcleranum=0;
		int mynubsel=0;
	 
    unsigned char key= KEY_NONE;
	
    board_init(); // ��ʼ���ڲ��Ĵ�������ɾ���˾���롣
    // ��ʼ��LCD4002Һ����
    lcd4002_init();
    // ��ʼ��INA226
    ina226_init();
    // ��ʱһ��ȷ����ʼ�����
    delay_ms(100);
		lcd4002_clear();
    while (1)
    {
			  
			  unsigned int j;
			  current = ina226_get_current();
				//��������ϵ��
				current /=1.11f;
				vol = ina226_get_bus_voltage();
				power = current * vol;
				power_get = ina226_get_power();
			  // ��ʼ��LCD4002Һ����
			  lcdcleranum++;
			  if(lcdcleranum>20)
        {
					lcd4002_clear();
					lcdcleranum=0;
				}
			  // ������ֵ��ʽ��Ϊ�ַ���
				sprintf(text_buffer, "I:%.3fA V:%.3fV P:%.3fW", current, vol, power);
				lcd4002_write_string_at(0, 1, text_buffer);
			  if(mymode==0)
			  sprintf(text_buffer, "MODE:%d NUMB:%d D:%dmm x:%dmm", mymode, mynubsel,mydistance, mysquarelength);
				else
				sprintf(text_buffer, "MODE:%d NUMB:%d D:?? x:??", mymode, mynubsel);
				lcd4002_write_string_at(0, 0, text_buffer);
			
			
      for (j = 0; j < 20; j++)
			{
				
				delay_ms(2);
					key = key_scan();
					if (key != KEY_NONE) 
					{
							switch (key) 
								{
									case '0': mynubsel=0; break;
									case '1': mynubsel=1; break;
									case '2': mynubsel=2; break;
									case '3': mynubsel=3; break;
									case '4': mynubsel=4; break;
									case '5': mynubsel=5; break;
									case '6': mynubsel=6; break;
									case '7': mynubsel=7; break;
									case '8': mynubsel=8; break;
									case '9': mynubsel=9; break;
									case 'A': mymode=1; break;
									case 'B': mymode=2; break;
									case 'C': mymode=3; break;
									case 'D': mymode=4; break;

								
							}
					}
			}
			//send 
			uart_putchar(DEBUG_UART,0x00);
			uart_putchar(DEBUG_UART,0xff);
			uart_putchar(DEBUG_UART,mymode);
			uart_putchar(DEBUG_UART,mynubsel);
			uart_putchar(DEBUG_UART,0xfe);
    }
}
