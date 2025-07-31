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
 
 
#include "board.h"
#include "zf_uart.h"
#include "zf_tim.h"
#include "zf_delay.h"


//22.11MHz��IRC�����Ĵ��� 0xFB
//24MHz��IRC�����Ĵ��� 0xFB
#define IRC_22M (*((uint8  idata*)0xFA))
#define IRC_24M (*((uint8  idata*)0xFB))

//ϵͳƵ�ʱ���
uint32 sys_clk = FOSC;



//-------------------------------------------------------------------------------------------------------------------
//  @brief      TST8H8K��ȡϵͳƵ��
//  @param      NULL          	��ֵ
//  @return     void        	ϵͳƵ��
//  Sample usage:               
//-------------------------------------------------------------------------------------------------------------------
uint32 get_clk(void)
{

	uint32 temp_count;
	P_SW2 |= 0x80;
	
	if(IRCBAND)
		temp_count = 36000000UL + ((int32)((int32)IRTRIM - (int32)IRC_22M) * 0x128E0UL); //Ƶ�ʵ�ƫ��,������������
	else
		temp_count = 24000000UL + ((int32)((int32)IRTRIM - (int32)IRC_24M) * 0xBB80UL);  //Ƶ�ʵ�ƫ��,������������
	
		temp_count /= CLKDIV;                              	  		//Ƶ��̫����Ҫ��Ƶ
	
	if 	(temp_count < 5764800UL)
		return 5529600UL;
	else if(temp_count < 8529600UL)
		return 6000000UL;
	else if(temp_count < 11529600UL)
		return 11059200UL;
	else if(temp_count < 15216000UL)
		return  12000000UL;
	else if(temp_count < 19216000UL)
		return  18432000UL;
	else if(temp_count < 21059200UL)
		return  20000000UL;
	else if(temp_count < 23059200UL)
		return  22118400UL;
	else if(temp_count < 25500000UL)
		return  24000000UL;
	else if(temp_count < 28500000UL)
		return  27000000UL;
	else if(temp_count < 31500000UL)
		return  30000000UL;
	else if(temp_count < 33500000UL)
		return  33177600UL;
	else if(temp_count < 35932000UL)
		return  35000000UL;
	else if(temp_count < 38432000UL)
		return  36864000UL;
	else if(temp_count < 42000000UL)
		return  40000000UL;
	else if(temp_count < 46000000UL)
		return  44236800UL;
	else 
		return 48000000UL;
}


//-------------------------------------------------------------------------------------------------------------------
//  @brief      STC8H8K����ϵͳƵ��
//  @param      NULL          	��ֵ
//  @return     void        	ϵͳƵ��
//  Sample usage:               
//-------------------------------------------------------------------------------------------------------------------
uint32 set_clk(void)
{
	
	P_SW2 |= 0x80;

	if(sys_clk == 22118400)
	{
		//ѡ�� 22.1184MHz
		CLKDIV = 0x04;
		IRTRIM = T22M_ADDR;
		VRTRIM = VRT27M_ADDR;
		IRCBAND = 0x02;
		CLKDIV = 0x00;
	}
	else if(sys_clk == 24000000)
	{
		//ѡ�� 24MHz
		CLKDIV = 0x04;
		IRTRIM = T24M_ADDR;
		VRTRIM = VRT27M_ADDR;
		IRCBAND = 0x02;
		CLKDIV = 0x00;
	}
	else if(sys_clk == 27000000)
	{
		//ѡ�� 27MHz
		CLKDIV = 0x04;
		IRTRIM = T27M_ADDR;
		VRTRIM = VRT27M_ADDR;
		IRCBAND = 0x02;
		CLKDIV = 0x00;
	}
	else if(sys_clk == 30000000)
	{
	
		//ѡ�� 30MHz
		CLKDIV = 0x04;
		IRTRIM = T30M_ADDR;
		VRTRIM = VRT27M_ADDR;
		IRCBAND = 0x02;
		CLKDIV = 0x00;
	}
	else if(sys_clk == 33177600)
	{
		//ѡ�� 33.1776MHz
		CLKDIV = 0x04;
		IRTRIM = T33M_ADDR;
		VRTRIM = VRT27M_ADDR;
		IRCBAND = 0x02;
		CLKDIV = 0x00;
	}
	else if(sys_clk == 35000000)
	{
		//ѡ�� 35MHz
		CLKDIV = 0x04;
		IRTRIM = T35M_ADDR;
		VRTRIM = VRT44M_ADDR;
		IRCBAND = 0x03;
		CLKDIV = 0x00;
	}
	else if(sys_clk == 44236800)
	{
		//ѡ�� 44.2368MHz
		CLKDIV = 0x04;
		IRTRIM = T44M_ADDR;
		VRTRIM = VRT44M_ADDR;
		IRCBAND = 0x03;
		CLKDIV = 0x00;
	}
	else if(sys_clk == 48000000)
	{
		//ѡ�� 48MHz
		CLKDIV = 0x04;
		IRTRIM = T48M_ADDR;
		VRTRIM = VRT44M_ADDR;
		IRCBAND = 0x03;
		CLKDIV = 0x00;
	}
	else
	{
		sys_clk = 44236800;
		//ѡ�� 44.2368MHz
		CLKDIV = 0x04;
		IRTRIM = T44M_ADDR;
		VRTRIM = VRT44M_ADDR;
		IRCBAND = 0x03;
		CLKDIV = 0x00;
	}

	return sys_clk;
}




void board_init(void)
{
	SET_P54_RESRT;
	P_SW2 = 0x80;


#if (1 == EXTERNAL_CRYSTA_ENABLE)
	XOSCCR = 0xc0; 			//�����ⲿ����
	while (!(XOSCCR & 1)); 	//�ȴ�ʱ���ȶ�
	CLKDIV = 0x00; 			//ʱ�Ӳ���Ƶ
	CKSEL = 0x01; 			//ѡ���ⲿ����
#else
	#if (0 == FOSC)
		// �Զ�����ϵͳƵ��
		// STC8H8K�汾 CHIPID31 = 0x5A
		if(CHIPID31 == 0x5A)
		{
			sys_clk = set_clk();
		}
		else	// TST8H8K�汾 CHIPID31 = 0x47
		{
			sys_clk = get_clk();
		}
	#else
		// �ֶ�����ϵͳƵ��
		sys_clk = FOSC;
	#endif
	
#endif

	delay_init();			//��ʱ������ʼ��
	
	P0M0 = 0x00;
	P0M1 = 0x00;
	P1M0 = 0x00;
	P1M1 = 0x00;
	P2M0 = 0x00;
	P2M1 = 0x00;
	P3M0 = 0x00;
	P3M1 = 0x00;
	P4M0 = 0x00;
	P4M1 = 0x00;
	P5M0 = 0x00;
	P5M1 = 0x00;
	P6M0 = 0x00;
	P6M1 = 0x00;
	P7M0 = 0x00;
	P7M1 = 0x00;
	



	ADCCFG = 0;
	AUXR = 0;
	SCON = 0;
	S2CON = 0;
	S3CON = 0;
	S4CON = 0;
	P_SW1 = 0;
	IE2 = 0;
	TMOD = 0;

	
	uart_init(DEBUG_UART, DEBUG_UART_RX_PIN, DEBUG_UART_TX_PIN, DEBUG_UART_BAUD, DEBUG_UART_TIM);
	
	EnableGlobalIRQ();		//�������ж�
}


#if (1 == PRINTF_ENABLE)      //��ʼ�����Դ���
//�ض���printf ���� ֻ�����uint16
char putchar(char c)
{
	uart_putchar(DEBUG_UART,(uint8)c);//���Լ�ʵ�ֵĴ��ڴ�ӡһ�ֽ����ݵĺ����滻������
	return c;
}
#endif

void DisableGlobalIRQ(void)
{
	EA = 0;
}


void EnableGlobalIRQ(void)
{
	EA = 1;
}

