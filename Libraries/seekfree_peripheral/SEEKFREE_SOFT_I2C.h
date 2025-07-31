/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2020,逐飞科技
 * All rights reserved.
 * 技术讨论QQ群：一群：179029047(已满)  二群：244861897(已满)  三群：824575535
 *
 * 以下所有内容版权均属逐飞科技所有，未经允许不得用于商业用途，
 * 欢迎各位使用并传播本程序，修改内容时必须保留逐飞科技的版权声明。
 *
 * @file       		软件模拟I2C
 * @company	   		成都逐飞科技有限公司
 * @author     		逐飞科技(QQ790875685)
 * @version    		查看doc内version文件 版本说明
 * @Software 		MDK FOR C51 V9.60
 * @Target core		STC8H8K64S4
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2020-06-01
 * @note		
					接线定义：
					------------------------------------ 
						SCL                 P1.5 (可修改)
						SDA                 P1.4 (可修改)
					------------------------------------ 
 ********************************************************************************************************************/

#ifndef _SEEKFREE_SOFT_I2C_H
#define _SEEKFREE_SOFT_I2C_H

#include "common.h"
#include "headfile.h"

// I2C引脚定义，用户可以根据需要修改
#define SOFT_I2C_SCL_PIN    P15
#define SOFT_I2C_SDA_PIN    P14

// I2C延时调节，用于调整I2C通信速度
#define SOFT_I2C_DELAY_TIME  5

// I2C通信状态定义
#define SOFT_I2C_ACK        0
#define SOFT_I2C_NACK       1
#define SOFT_I2C_SUCCESS    0
#define SOFT_I2C_FAIL       1

// 函数声明
void soft_i2c_init(void);
void soft_i2c_start(void);
void soft_i2c_stop(void);
void soft_i2c_send_ack(uint8 ack);
uint8 soft_i2c_wait_ack(void);
void soft_i2c_send_byte(uint8 dat);
uint8 soft_i2c_read_byte(uint8 ack);
uint8 soft_i2c_write_reg(uint8 dev_addr, uint8 reg_addr, uint8 dat);
uint8 soft_i2c_read_reg(uint8 dev_addr, uint8 reg_addr);
uint8 soft_i2c_write_bytes(uint8 dev_addr, uint8 reg_addr, uint8 *dat, uint8 len);
uint8 soft_i2c_read_bytes(uint8 dev_addr, uint8 reg_addr, uint8 *dat, uint8 len);
uint8 soft_i2c_write_byte_direct(uint8 dev_addr, uint8 dat);

#endif 