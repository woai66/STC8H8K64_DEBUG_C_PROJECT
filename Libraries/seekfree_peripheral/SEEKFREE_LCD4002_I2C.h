/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2020,逐飞科技
 * All rights reserved.
 * 技术讨论QQ群：一群：179029047(已满)  二群：244861897(已满)  三群：824575535
 *
 * 以下所有内容版权均属逐飞科技所有，未经允许不得用于商业用途，
 * 欢迎各位使用并传播本程序，修改内容时必须保留逐飞科技的版权声明。
 *
 * @file       		LCD4002液晶屏I2C驱动
 * @company	   		成都逐飞科技有限公司
 * @author     		逐飞科技(QQ790875685)
 * @version    		查看doc内version文件 版本说明
 * @Software 		MDK FOR C51 V9.60
 * @Target core		STC8H8K64S4
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2020-06-01
 * @note		
					LCD4002液晶屏通过PCF8574扩展芯片连接：
					------------------------------------
						SCL                 P1.5 (连接到PCF8574的SCL)
						SDA                 P1.4 (连接到PCF8574的SDA)
						VCC                 5V
						GND                 GND
					------------------------------------
					PCF8574引脚定义：
					P0 -> RS  (Register Select)
					P1 -> RW  (Read/Write)
					P2 -> E   (Enable)
					P3 -> BL  (Backlight)
					P4 -> D4  (Data bit 4)
					P5 -> D5  (Data bit 5)
					P6 -> D6  (Data bit 6)
					P7 -> D7  (Data bit 7)
 ********************************************************************************************************************/

#ifndef _SEEKFREE_LCD4002_I2C_H
#define _SEEKFREE_LCD4002_I2C_H

#include "common.h"
#include "headfile.h"

// LCD4002默认I2C地址 (PCF8574默认地址0x27)
#define LCD4002_I2C_ADDR    0x27

// PCF8574引脚位定义
#define LCD4002_RS          0x01    // P0
#define LCD4002_RW          0x02    // P1  
#define LCD4002_E           0x04    // P2
#define LCD4002_BL          0x08    // P3 (背光)
#define LCD4002_D4          0x10    // P4
#define LCD4002_D5          0x20    // P5
#define LCD4002_D6          0x40    // P6
#define LCD4002_D7          0x80    // P7

// LCD命令定义
#define LCD4002_CMD_CLEAR           0x01    // 清屏
#define LCD4002_CMD_HOME            0x02    // 光标回到原点
#define LCD4002_CMD_ENTRY_MODE      0x06    // 输入模式设置
#define LCD4002_CMD_DISPLAY_ON      0x0C    // 显示开，光标关，闪烁关
#define LCD4002_CMD_DISPLAY_OFF     0x08    // 关闭显示
#define LCD4002_CMD_CURSOR_ON       0x0E    // 显示开，光标开，闪烁关
#define LCD4002_CMD_CURSOR_BLINK    0x0F    // 显示开，光标开，闪烁开
#define LCD4002_CMD_FUNCTION_SET    0x28    // 4位数据，2行，5×8字符
#define LCD4002_CMD_SET_CGRAM       0x40    // 设置CGRAM地址
#define LCD4002_CMD_SET_DDRAM       0x80    // 设置DDRAM地址

// 特殊字符定义
#define LCD4002_CHAR_DEGREE         0xDF    // 度符号 °

// 函数声明
void lcd4002_init(void);
void lcd4002_backlight(uint8 state);
void lcd4002_clear(void);
void lcd4002_home(void);
void lcd4002_set_cursor(uint8 col, uint8 row);
void lcd4002_write_char(uint8 dat);
void lcd4002_write_string(char *str);
void lcd4002_write_string_at(uint8 col, uint8 row, char *str);
void lcd4002_write_number(int32 num);
void lcd4002_write_number_at(uint8 col, uint8 row, int32 num);
void lcd4002_write_float(float num, uint8 decimal_places);
void lcd4002_write_float_at(uint8 col, uint8 row, float num, uint8 decimal_places);
void lcd4002_create_char(uint8 location, uint8 charmap[]);
void lcd4002_display_char(uint8 location);

#endif 