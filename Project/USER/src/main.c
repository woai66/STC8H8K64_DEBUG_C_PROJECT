/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2020,逐飞科技
 * All rights reserved.
 * 技术讨论QQ群：一群：179029047(已满)  二群：244861897(已满)  三群：824575535
 *
 * 以下所有内容版权均属逐飞科技所有，未经允许不得用于商业用途，
 * 欢迎各位使用并传播本程序，修改内容时必须保留逐飞科技的版权声明。
 *
 * @file       		main
 * @company	   		成都逐飞科技有限公司
 * @author     		逐飞科技(QQ790875685)
 * @version    		查看doc内version文件 版本说明
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
 * 系统频率，可查看board.h中的 FOSC 宏定义修改。
 * board.h文件中FOSC的值设置为0,则程序自动设置系统频率为44.2368MHZ
 * 在board_init中,已经将P54引脚设置为复位
 * 如果需要使用P54引脚,可以在board.c文件中的board_init()函数中删除SET_P54_RESRT即可
 */

/*
 * LCD4002液晶屏连接说明：
 * ====================================
 * LCD4002模块 -----> STC8H8K64单片机
 * ====================================
 * VCC        -----> 5V (或3.3V，根据模块电压)
 * GND        -----> GND
 * SDA        -----> P14 (软件I2C数据线)
 * SCL        -----> P15 (软件I2C时钟线)
 * ====================================
 * 
 * 注意事项：
 * 1. 确保LCD4002模块的I2C地址为0x27（默认地址）
 * 2. 如果地址不同，请修改SEEKFREE_LCD4002_I2C.h中的LCD4002_I2C_ADDR定义
 * 3. 如果需要修改I2C引脚，请修改SEEKFREE_SOFT_I2C.h中的引脚定义
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
	
    board_init(); // 初始化内部寄存器，勿删除此句代码。
    // 初始化LCD4002液晶屏
    lcd4002_init();
    // 初始化INA226
    ina226_init();
    // 延时一下确保初始化完成
    delay_ms(100);
		lcd4002_clear();
    while (1)
    {
			  
			  unsigned int j;
			  current = ina226_get_current();
				//电流矫正系数
				current /=1.11f;
				vol = ina226_get_bus_voltage();
				power = current * vol;
				power_get = ina226_get_power();
			  // 初始化LCD4002液晶屏
			  lcdcleranum++;
			  if(lcdcleranum>20)
        {
					lcd4002_clear();
					lcdcleranum=0;
				}
			  // 将电流值格式化为字符串
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
