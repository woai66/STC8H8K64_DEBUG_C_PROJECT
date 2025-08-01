/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2020,逐飞科技
 * All rights reserved.
 * 技术讨论QQ群：一群：179029047(已满)  二群：244861897(已满)  三群：824575535
 *
 * 以下所有内容版权均属逐飞科技所有，未经允许不得用于商业用途，
 * 欢迎各位使用并传播本程序，修改内容时必须保留逐飞科技的版权声明。
 *
 * @file       		isr
 * @company	   		成都逐飞科技有限公司
 * @author     		逐飞科技(QQ790875685)
 * @version    		查看doc内version文件 版本说明
 * @Software 		MDK FOR C51 V9.60
 * @Target core		STC8H8K64S4
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2020-4-14
 ********************************************************************************************************************/
#include "headfile.h"


volatile bit new_data_ready = 0;

enum {
    STATE_WAIT_HEADER1,   // ?????1 (0x00)
    STATE_WAIT_HEADER2,   // ?????2 (0xFF)
    STATE_READ_DISTANCE,  // ????
    STATE_READ_LENGTH,    // ????
    STATE_WAIT_FOOTER     // ????? (0xFE)
} protocol_state = STATE_WAIT_HEADER1;

void ParseUART_Protocol(unsigned char rx_data) {
    static unsigned char temp_distance, temp_length;
    
    switch(protocol_state) {
        case STATE_WAIT_HEADER1:
            if(rx_data == 0x00) {
                protocol_state = STATE_WAIT_HEADER2;
            }
            break;
            
        case STATE_WAIT_HEADER2:
            if(rx_data == 0xFF) {
                protocol_state = STATE_READ_DISTANCE;
            } else {
                protocol_state = STATE_WAIT_HEADER1; // ????,????
            }
            break;
            
        case STATE_READ_DISTANCE:
            temp_distance = rx_data;
            protocol_state = STATE_READ_LENGTH;
            break;
            
        case STATE_READ_LENGTH:
            temp_length = rx_data;
            protocol_state = STATE_WAIT_FOOTER;
            break;
            
        case STATE_WAIT_FOOTER:
            if(rx_data == 0xFE) {
                // ???????
                mydistance = temp_distance;
                mysquarelength = temp_length;
						    mymode=0;
                new_data_ready = 1;  // ????????
            }
            protocol_state = STATE_WAIT_HEADER1; // ???????????
            break;
            
        default:
            protocol_state = STATE_WAIT_HEADER1;
    }
}
//UART1中断
void UART1_Isr() interrupt 4
{

	
	
    if(UART1_GET_TX_FLAG)
    {
        UART1_CLEAR_TX_FLAG;
        busy[1] = 0;
    }
    if(UART1_GET_RX_FLAG)
    {
			  
        UART1_CLEAR_RX_FLAG;
        ParseUART_Protocol(SBUF); // ????????
    }
}

//UART2中断
void UART2_Isr() interrupt 8
{
    if(UART2_GET_TX_FLAG)
	{
        UART2_CLEAR_TX_FLAG;
		busy[2] = 0;
	}
    if(UART2_GET_RX_FLAG)
	{
        UART2_CLEAR_RX_FLAG;
		//接收数据寄存器为：S2BUF

	}
}


//UART3中断
void UART3_Isr() interrupt 17
{
    if(UART3_GET_TX_FLAG)
	{
        UART3_CLEAR_TX_FLAG;
		busy[3] = 0;
	}
    if(UART3_GET_RX_FLAG)
	{
        UART3_CLEAR_RX_FLAG;
		//接收数据寄存器为：S3BUF

	}
}


//UART4中断
void UART4_Isr() interrupt 18
{
    if(UART4_GET_TX_FLAG)
	{
        UART4_CLEAR_TX_FLAG;
		busy[4] = 0;
	}
    if(UART4_GET_RX_FLAG)
	{
        UART4_CLEAR_RX_FLAG;
        
		//接收数据寄存器为：S4BUF;
        if(wireless_type == WIRELESS_SI24R1)
            wireless_uart_callback();           //无线转串口回调函数
        else if(wireless_type == WIRELESS_CH9141)
            bluetooth_ch9141_uart_callback();   //蓝牙转串口回调函数
        else if(wireless_type == WIRELESS_CH573)
            wireless_ch573_callback();          //CH573模块回调函数
        
	}
}

#define LED P52
void INT0_Isr() interrupt 0
{
	LED = 0;	//点亮LED
}
void INT1_Isr() interrupt 2
{

}
void INT2_Isr() interrupt 10
{
	INT2_CLEAR_FLAG;  //清除中断标志
}
void INT3_Isr() interrupt 11
{
	INT3_CLEAR_FLAG;  //清除中断标志
}

void INT4_Isr() interrupt 16
{
	INT4_CLEAR_FLAG;  //清除中断标志
}

void TM0_Isr() interrupt 1
{

}
void TM1_Isr() interrupt 3
{

}
void TM2_Isr() interrupt 12
{
	TIM2_CLEAR_FLAG;  //清除中断标志
	
}
void TM3_Isr() interrupt 19
{
	TIM3_CLEAR_FLAG; //清除中断标志
	
}

void TM4_Isr() interrupt 20
{
	TIM4_CLEAR_FLAG; //清除中断标志
	ccd_collect();	 //CCD采集数据

}

//void  INT0_Isr()  interrupt 0;
//void  TM0_Isr()   interrupt 1;
//void  INT1_Isr()  interrupt 2;
//void  TM1_Isr()   interrupt 3;
//void  UART1_Isr() interrupt 4;
//void  ADC_Isr()   interrupt 5;
//void  LVD_Isr()   interrupt 6;
//void  PCA_Isr()   interrupt 7;
//void  UART2_Isr() interrupt 8;
//void  SPI_Isr()   interrupt 9;
//void  INT2_Isr()  interrupt 10;
//void  INT3_Isr()  interrupt 11;
//void  TM2_Isr()   interrupt 12;
//void  INT4_Isr()  interrupt 16;
//void  UART3_Isr() interrupt 17;
//void  UART4_Isr() interrupt 18;
//void  TM3_Isr()   interrupt 19;
//void  TM4_Isr()   interrupt 20;
//void  CMP_Isr()   interrupt 21;
//void  I2C_Isr()   interrupt 24;
//void  USB_Isr()   interrupt 25;
//void  PWM1_Isr()  interrupt 26;
//void  PWM2_Isr()  interrupt 27;