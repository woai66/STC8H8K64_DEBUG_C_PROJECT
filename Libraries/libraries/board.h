/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2020,逐飞科技
 * All rights reserved.
 * 技术讨论QQ群：一群：179029047(已满)  二群：244861897(已满)  三群：824575535
 *
 * 以下所有内容版权均属逐飞科技所有，未经允许不得用于商业用途，
 * 欢迎各位使用并传播本程序，修改内容时必须保留逐飞科技的版权声明。
 *
 * @file       		board
 * @company	   		成都逐飞科技有限公司
 * @author     		逐飞科技(QQ790875685)
 * @version    		查看doc内version文件 版本说明
 * @Software 		MDK FOR C51 V9.60
 * @Target core		STC8H8K64S4
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2020-4-14
 ********************************************************************************************************************/



#ifndef __BOARD_H
#define __BOARD_H
#include "common.h"


#define FOSC					11059200			// FOSC的值设置为0，则内核频率通过寄存器强制设置为44.2368Mhz,，
											// 不管STC-ISP软件下载时候选择多少，他都是44.2368Mhz。
											
//#define FOSC          		44236800	// FOSC的值设置为44.2368Mhz,
											// 使用STC-ISP软件下载的时候，
											// 此频率需要跟STC-ISP软件中的 <输入用户程序运行时的IRC频率>选项的频率一致。
											
#define EXTERNAL_CRYSTA_ENABLE 	0			// 使用外部晶振，0为不使用，1为使用（建议使用内部晶振）
#define PRINTF_ENABLE			1			// printf使能，0为失能，1为使能
#define ENABLE_IAP 				1			// 使能软件一键下载功能，0为失能，1为使能
#define	PERIPHERAL_PIN_SWITCH	1			// 0为48脚核心板，1为64脚核心板

#define DEBUG_UART 			  	UART_1
#define DEBUG_UART_BAUD 	  	115200
#define DEBUG_UART_RX_PIN  		UART1_RX_P36
#define DEBUG_UART_TX_PIN  		UART1_TX_P37
#define DEBUG_UART_TIM			TIM_2

// 其他可选串口配置示例：
// 使用UART2 + P10/P11:
// #define DEBUG_UART 			  	UART_2
// #define DEBUG_UART_RX_PIN  		UART2_RX_P10
// #define DEBUG_UART_TX_PIN  		UART2_TX_P11

// 使用UART3 + P00/P01:
// #define DEBUG_UART 			  	UART_3
// #define DEBUG_UART_RX_PIN  		UART3_RX_P00
// #define DEBUG_UART_TX_PIN  		UART3_TX_P01

#if (1==PRINTF_ENABLE)
	char putchar(char c);
#endif

#define SET_P54_RESRT 	  (RSTCFG |= 1<<4)	//设置P54为复位引脚

extern uint32 sys_clk;

void board_init(void);
void DisableGlobalIRQ(void);
void EnableGlobalIRQ(void);

#endif

