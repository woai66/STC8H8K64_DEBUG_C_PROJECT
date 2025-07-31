/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2020,逐飞科技
 * All rights reserved.
 * 技术讨论QQ群：一群：179029047(已满)  二群：244861897(已满)  三群：824575535
 *
 * 以下所有内容版权均属逐飞科技所有，未经允许不得用于商业用途，
 * 欢迎各位使用并传播本程序，修改内容时必须保留逐飞科技的版权声明。
 *
 * @file       		pwm
 * @company	   		成都逐飞科技有限公司
 * @author     		逐飞科技(QQ790875685)
 * @version    		查看doc内version文件 版本说明
 * @Software 		MDK FOR C51 V9.60
 * @Target core		STC8H8K64S4
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2020-4-14
 ********************************************************************************************************************/

#ifndef __ZF_PWM_H
#define __ZF_PWM_H
#include "common.h"


#define PWM_DUTY_MAX 10000



//此PWM模块是单独的模块。跟TIMER没有关系。
typedef enum
{
	//PWM1-PWM4为一组PWM，可以使用多个通道的不同引脚输出PWM，但是同一组引脚频率必须一致
	//PWM1通道只允许使用其中一个。
	PWM1P_P10 = 0x00,PWM1N_P11,
	PWM1P_P20,		 PWM1N_P21,
	PWM1P_P60,		 PWM1N_P61,
	//PWM2通道只允许使用其中一个。
	PWM2P_P12 = 0x10,//该引脚已做 USB 内核电源稳压脚
	PWM2N_P13,
	PWM2P_P22,		 PWM2N_P23,
	PWM2P_P62,		 PWM2N_P63,
	//PWM3通道只允许使用其中一个。
	PWM3P_P14 = 0x20,PWM3N_P15,
	PWM3P_P24,		 PWM3N_P25,
	PWM3P_P64,		 PWM3N_P65,
	//PWM4通道只允许使用其中一个。
	PWM4P_P16 = 0x30,PWM4N_P17,
	PWM4P_P26,		 PWM4N_P27,
	PWM4P_P66,		 PWM4N_P67,
	PWM4P_P34,		 PWM4N_P33,
	
	//PWM5-PWM8为一组PWM，可以使用多个通道的不同引脚输出PWM，但是同一组引脚频率必须一致
	//PWM5通道只允许使用其中一个。
	PWM5_P20 = 0x40,
	PWM5_P17,
	PWM5_P00,
	PWM5_P74,
	//PWM6通道只允许使用其中一个。
	PWM6_P21 = 0x50,
	PWM6_P54,
	PWM6_P01,
	PWM6_P75,
	//PWM7通道只允许使用其中一个。
	PWM7_P22 = 0x60,
	PWM7_P33,
	PWM7_P02,
	PWM7_P76,
	//PWM8通道只允许使用其中一个。
	PWM8_P23 = 0x70,
	PWM8_P34,
	PWM8_P03,
	PWM8_P77,

}PWMCH_enum;


void pwm_init(PWMCH_enum pwmch,uint32 freq, uint16 duty);
void pwm_duty(PWMCH_enum pwmch, uint16 duty);
void pwm_freq(PWMCH_enum pwmch, uint32 freq, uint16 duty);


#endif
