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
 ********************************************************************************************************************/

#include "SEEKFREE_LCD4002_I2C.h"
#include "SEEKFREE_SOFT_I2C.h"
#include "zf_delay.h"
#include <stdio.h>

// 全局变量
static uint8 lcd_backlight_state = LCD4002_BL;  // 背光状态，默认开启

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002写入4位数据到PCF8574
//  @param      dat            要写入的4位数据
//  @param      rs              RS信号状态 (0:命令, 1:数据)
//  @return     void
//  @since      v1.0
//  Sample usage:               内部调用
//-------------------------------------------------------------------------------------------------------------------
static void lcd4002_write_4bits(uint8 dat, uint8 rs)
{
    uint8 pcf_data = 0;
    
    // 组装PCF8574数据
    pcf_data = lcd_backlight_state;  // 背光状态
    if(rs) pcf_data |= LCD4002_RS;   // RS信号
    
    // 设置高4位数据
    if(dat & 0x08) pcf_data |= LCD4002_D7;
    if(dat & 0x04) pcf_data |= LCD4002_D6;
    if(dat & 0x02) pcf_data |= LCD4002_D5;
    if(dat & 0x01) pcf_data |= LCD4002_D4;
    
    // 发送数据，E信号低电平
    soft_i2c_write_byte_direct(LCD4002_I2C_ADDR, pcf_data);
    delay_us(1);
    
    // 发送数据，E信号高电平
    soft_i2c_write_byte_direct(LCD4002_I2C_ADDR, pcf_data | LCD4002_E);
    delay_us(1);
    
    // 发送数据，E信号低电平
    soft_i2c_write_byte_direct(LCD4002_I2C_ADDR, pcf_data);
    delay_us(50);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002写入8位数据
//  @param      dat            要写入的8位数据
//  @param      rs              RS信号状态 (0:命令, 1:数据)
//  @return     void
//  @since      v1.0
//  Sample usage:               内部调用
//-------------------------------------------------------------------------------------------------------------------
static void lcd4002_write_byte(uint8 dat, uint8 rs)
{
    lcd4002_write_4bits(dat >> 4, rs);    // 发送高4位
    lcd4002_write_4bits(dat & 0x0F, rs);  // 发送低4位
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002发送命令
//  @param      cmd             要发送的命令
//  @return     void
//  @since      v1.0
//  Sample usage:               内部调用
//-------------------------------------------------------------------------------------------------------------------
static void lcd4002_write_command(uint8 cmd)
{
    lcd4002_write_byte(cmd, 0);  // RS=0表示命令
    if(cmd == LCD4002_CMD_CLEAR || cmd == LCD4002_CMD_HOME)
        delay_ms(2);  // 清屏和复位命令需要更长的延时
    else
        delay_us(40);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002发送数据
//  @param      dat            要发送的数据
//  @return     void
//  @since      v1.0
//  Sample usage:               内部调用
//-------------------------------------------------------------------------------------------------------------------
static void lcd4002_write_data(uint8 dat)
{
    lcd4002_write_byte(dat, 1);  // RS=1表示数据
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002初始化
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_init();
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_init(void)
{
    // 初始化软件I2C
    soft_i2c_init();
    
    // 等待LCD上电稳定
    delay_ms(50);
    
    // LCD初始化序列 (HD44780标准初始化)
    // 发送0x03三次，确保进入8位模式
    lcd4002_write_4bits(0x03, 0);
    delay_ms(5);
    lcd4002_write_4bits(0x03, 0);
    delay_us(150);
    lcd4002_write_4bits(0x03, 0);
    delay_us(150);
    
    // 切换到4位模式
    lcd4002_write_4bits(0x02, 0);
    delay_us(150);
    
    // 功能设置：4位数据，2行显示，5×8字符
    lcd4002_write_command(LCD4002_CMD_FUNCTION_SET);
    
    // 关闭显示
    lcd4002_write_command(LCD4002_CMD_DISPLAY_OFF);
    
    // 清屏
    lcd4002_write_command(LCD4002_CMD_CLEAR);
    
    // 输入模式设置：光标右移，不移屏
    lcd4002_write_command(LCD4002_CMD_ENTRY_MODE);
    
    // 开启显示，关闭光标和闪烁
    lcd4002_write_command(LCD4002_CMD_DISPLAY_ON);
    
    // 开启背光
    lcd4002_backlight(1);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002背光控制
//  @param      state           背光状态 (0:关闭, 1:开启)
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_backlight(1);
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_backlight(uint8 state)
{
    if(state)
        lcd_backlight_state = LCD4002_BL;
    else
        lcd_backlight_state = 0;
    
    // 发送当前背光状态
    soft_i2c_write_byte_direct(LCD4002_I2C_ADDR, lcd_backlight_state);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002清屏
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_clear();
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_clear(void)
{
    lcd4002_write_command(LCD4002_CMD_CLEAR);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002光标回到原点
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_home();
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_home(void)
{
    lcd4002_write_command(LCD4002_CMD_HOME);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002设置光标位置
//  @param      col             列位置 (0-39)
//  @param      row             行位置 (0-1)
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_set_cursor(0, 0);
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_set_cursor(uint8 col, uint8 row)
{
    uint8 address;
    
    if(row == 0)
        address = 0x00 + col;  // 第一行
    else
        address = 0x40 + col;  // 第二行
    
    lcd4002_write_command(LCD4002_CMD_SET_DDRAM | address);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002写入单个字符
//  @param      dat            要写入的字符
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_write_char('A');
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_write_char(uint8 dat)
{
    lcd4002_write_data(dat);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002写入字符串
//  @param      str             要写入的字符串
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_write_string("Hello World");
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_write_string(char *str)
{
    while(*str)
    {
        lcd4002_write_char(*str++);
    }
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002在指定位置写入字符串
//  @param      col             列位置 (0-39)
//  @param      row             行位置 (0-1)
//  @param      str             要写入的字符串
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_write_string_at(0, 0, "Hello");
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_write_string_at(uint8 col, uint8 row, char *str)
{
    lcd4002_set_cursor(col, row);
    lcd4002_write_string(str);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002写入整数
//  @param      num             要写入的整数
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_write_number(1234);
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_write_number(int32 num)
{
    char str[12];
    sprintf(str, "%ld", num);
    lcd4002_write_string(str);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002在指定位置写入整数
//  @param      col             列位置 (0-39)
//  @param      row             行位置 (0-1)
//  @param      num             要写入的整数
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_write_number_at(10, 1, 5678);
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_write_number_at(uint8 col, uint8 row, int32 num)
{
    lcd4002_set_cursor(col, row);
    lcd4002_write_number(num);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002写入浮点数
//  @param      num             要写入的浮点数
//  @param      decimal_places  小数位数
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_write_float(3.14159, 2);
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_write_float(float num, uint8 decimal_places)
{
    char str[16];
    char format[8];
    
    sprintf(format, "%%.%df", decimal_places);
    sprintf(str, format, num);
    lcd4002_write_string(str);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002在指定位置写入浮点数
//  @param      col             列位置 (0-39)
//  @param      row             行位置 (0-1)
//  @param      num             要写入的浮点数
//  @param      decimal_places  小数位数
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_write_float_at(0, 1, 2.718, 3);
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_write_float_at(uint8 col, uint8 row, float num, uint8 decimal_places)
{
    lcd4002_set_cursor(col, row);
    lcd4002_write_float(num, decimal_places);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002创建自定义字符
//  @param      location        字符位置 (0-7)
//  @param      charmap         字符点阵数据 (8字节)
//  @return     void
//  @since      v1.0
//  Sample usage:               uint8 heart[8] = {0x00,0x0A,0x1F,0x1F,0x0E,0x04,0x00,0x00};
//                              lcd4002_create_char(0, heart);
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_create_char(uint8 location, uint8 charmap[])
{
    uint8 i;
    location &= 0x07;  // 限制在0-7范围内
    
    lcd4002_write_command(LCD4002_CMD_SET_CGRAM | (location << 3));
    for(i = 0; i < 8; i++)
    {
        lcd4002_write_data(charmap[i]);
    }
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      LCD4002显示自定义字符
//  @param      location        字符位置 (0-7)
//  @return     void
//  @since      v1.0
//  Sample usage:               lcd4002_display_char(0);
//-------------------------------------------------------------------------------------------------------------------
void lcd4002_display_char(uint8 location)
{
    lcd4002_write_char(location);
} 