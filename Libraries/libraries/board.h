/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2020,��ɿƼ�
 * All rights reserved.
 * ��������QQȺ��һȺ��179029047(����)  ��Ⱥ��244861897(����)  ��Ⱥ��824575535
 *
 * �����������ݰ�Ȩ������ɿƼ����У�δ��������������ҵ��;��
 * ��ӭ��λʹ�ò������������޸�����ʱ���뱣����ɿƼ��İ�Ȩ������
 *
 * @file       		board
 * @company	   		�ɶ���ɿƼ����޹�˾
 * @author     		��ɿƼ�(QQ790875685)
 * @version    		�鿴doc��version�ļ� �汾˵��
 * @Software 		MDK FOR C51 V9.60
 * @Target core		STC8H8K64S4
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2020-4-14
 ********************************************************************************************************************/



#ifndef __BOARD_H
#define __BOARD_H
#include "common.h"


#define FOSC					44236800			// FOSC��ֵ����Ϊ0�����ں�Ƶ��ͨ���Ĵ���ǿ������Ϊ44.2368Mhz,��
											// ����STC-ISP�������ʱ��ѡ����٣�������44.2368Mhz��
											
//#define FOSC          		44236800	// FOSC��ֵ����Ϊ44.2368Mhz,
											// ʹ��STC-ISP������ص�ʱ��
											// ��Ƶ����Ҫ��STC-ISP����е� <�����û���������ʱ��IRCƵ��>ѡ���Ƶ��һ�¡�
											
#define EXTERNAL_CRYSTA_ENABLE 	0			// ʹ���ⲿ����0Ϊ��ʹ�ã�1Ϊʹ�ã�����ʹ���ڲ�����
#define PRINTF_ENABLE			1			// printfʹ�ܣ�0Ϊʧ�ܣ�1Ϊʹ��
#define ENABLE_IAP 				1			// ʹ�����һ�����ع��ܣ�0Ϊʧ�ܣ�1Ϊʹ��
#define	PERIPHERAL_PIN_SWITCH	1			// 0Ϊ48�ź��İ壬1Ϊ64�ź��İ�

#define DEBUG_UART 			  	UART_1
#define DEBUG_UART_BAUD 	  	115200
#define DEBUG_UART_RX_PIN  		UART1_RX_P30
#define DEBUG_UART_TX_PIN  		UART1_TX_P31
#define DEBUG_UART_TIM			TIM_2

#if (1==PRINTF_ENABLE)
	char putchar(char c);
#endif

#define SET_P54_RESRT 	  (RSTCFG |= 1<<4)	//����P54Ϊ��λ����

extern uint32 sys_clk;

void board_init(void);
void DisableGlobalIRQ(void);
void EnableGlobalIRQ(void);

#endif

