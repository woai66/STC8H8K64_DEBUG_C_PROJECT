/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2020,逐飞科技
 * All rights reserved.
 * 技术讨论QQ群：一群：179029047(已满)  二群：244861897(已满)  三群：824575535
 *
 * 以下所有内容版权均属逐飞科技所有，未经允许不得用于商业用途，
 * 欢迎各位使用并传播本程序，修改内容时必须保留逐飞科技的版权声明。
 *
 * @file       		总头文件
 * @company	   		成都逐飞科技有限公司
 * @author     		逐飞科技(QQ790875685)
 * @version    		查看doc内version文件 版本说明
 * @Software 		MDK FOR C51 V9.60
 * @Target core		STC8H8K64S4
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2020-4-14
 ********************************************************************************************************************/

#ifndef _headfile_H
#define _headfile_H

#include "common.h"
#include "board.h"
#include "zf_delay.h"
#include "zf_nvic.h"
#include "zf_tim.h"
#include "zf_pwm.h"
#include "zf_gpio.h"
#include "zf_uart.h"
#include "zf_spi.h"
#include "zf_iic.h"
#include "zf_adc.h"
#include "zf_exti.h"
#include "zf_eeprom.h"
#include "zf_fifo.h"
#include "zf_mdu16.h"

#include "seekfree_assistant.h"

#include "SEEKFREE_18TFT.h"
#include "SEEKFREE_ABSOLUTE_ENCODER.h"
#include "SEEKFREE_BLUETOOTH_CH9141.h"
#include "SEEKFREE_DL1A.h"
#include "SEEKFREE_DL1B.h"
#include "SEEKFREE_FONT.h"
#include "SEEKFREE_ICM20602.h"
#include "SEEKFREE_IIC.h"
#include "SEEKFREE_IMU660RA.h"
#include "SEEKFREE_IMU963RA.h"
#include "SEEKFREE_IPS114_SPI.h"
#include "SEEKFREE_MPU6050.h"
#include "SEEKFREE_OLED.h"
#include "SEEKFREE_PRINTF.h"
#include "SEEKFREE_TSL1401.h"
#include "SEEKFREE_VIRSCO.h"
#include "SEEKFREE_WIRELESS.h"
#include "SEEKFREE_WIRELESS_CH573.h"
#include "SEEKFREE_SOFT_I2C.h"
#include "SEEKFREE_LCD4002_I2C.h"
#include "SEEKFREE_INA226.h"

extern volatile int mymode;
extern volatile int mydistance;
extern volatile int mysquarelength;
extern volatile unsigned char distance;  // 距离值
extern volatile unsigned char length;    // 长度值
extern volatile bit new_data_ready;      // 新数据就绪标志

#endif
