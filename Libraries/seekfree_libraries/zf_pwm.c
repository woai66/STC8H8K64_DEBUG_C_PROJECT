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
 * @Software 		MDK5.27
 * @Target core		STC8H8K64S4
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2020-4-14
 ********************************************************************************************************************/

#include "zf_pwm.h"
#include "board.h"
#include "zf_gpio.h"
#include "zf_uart.h"
#include "stdio.h"



#define PWM1_CCMR1_ADDR  0xfec8	//CCMR2_ADDR = CCMR1_ADDR + 1
#define PWM1_CCR1_ADDR   0xfed5 //CCR2_ADDR = CCR1_ADDR + 2
#define PWM1_CCER1_ADDR  0xfecc //CCER2_ADDR = CCER1_ADDR + 1

#define PWM2_CCMR1_ADDR  0xfee8 //CCMR2_ADDR = CCMR1_ADDR + 1
#define PWM2_CCR1_ADDR   0xfef5	//CCR2_ADDR = CCR1_ADDR + 2
#define	PWM2_CCER1_ADDR  0xfeec //CCER2_ADDR = CCER1_ADDR + 1

//-------------------------------------------------------------------------------------------------------------------
//  @brief      PWM_gpio初始化（内部使用用户无需关心）
//  @param      pwmch       PWM通道号及引脚
//  @return     void
//  Sample usage:           
//-------------------------------------------------------------------------------------------------------------------
void pwm_set_gpio(PWMCH_enum pwmch)
{
	switch(pwmch)
	{
		case PWM1P_P10:
		{
			gpio_mode(P1_0,GPO_PP);
			break;
		}
		case PWM1N_P11:
		{
			gpio_mode(P1_1,GPO_PP);
			break;
		}
		case PWM1P_P20:
		{
			gpio_mode(P2_0,GPO_PP);
			break;
		}
		case PWM1N_P21:
		{
			gpio_mode(P2_1,GPO_PP);
			break;
		}
		case PWM1P_P60:
		{
			gpio_mode(P6_0,GPO_PP);
			break;
		}
		case PWM1N_P61:
		{
			gpio_mode(P6_1,GPO_PP);
			break;
		}
		
		case PWM2P_P12:
		{
			gpio_mode(P1_2,GPO_PP);
			break;
		}
		case PWM2N_P13:
		{
			gpio_mode(P1_3,GPO_PP);
			break;
		}
		case PWM2P_P22:
		{
			gpio_mode(P2_2,GPO_PP);
			break;
		}
		case PWM2N_P23:
		{
			gpio_mode(P2_3,GPO_PP);
			break;
		}
		case PWM2P_P62:
		{
			gpio_mode(P6_2,GPO_PP);
			break;
		}
		case PWM2N_P63:
		{
			gpio_mode(P6_3,GPO_PP);
			break;
		}
		
		case PWM3P_P14:
		{
			gpio_mode(P1_4,GPO_PP);
			break;
		}
		case PWM3N_P15:
		{
			gpio_mode(P1_5,GPO_PP);
			break;
		}
		case PWM3P_P24:
		{
			gpio_mode(P2_4,GPO_PP);
			break;
		}
		case PWM3N_P25:
		{
			gpio_mode(P2_5,GPO_PP);
			break;
		}
		case PWM3P_P64:
		{
			gpio_mode(P6_4,GPO_PP);
			break;
		}
		case PWM3N_P65:
		{
			gpio_mode(P6_5,GPO_PP);
			break;
		}
		
		
		case PWM4P_P16:
		{
			gpio_mode(P1_6,GPO_PP);
			break;
		}
		case PWM4N_P17:
		{
			gpio_mode(P1_7,GPO_PP);
			break;
		}
		case PWM4P_P26:
		{
			gpio_mode(P2_6,GPO_PP);
			break;
		}
		case PWM4N_P27:
		{
			gpio_mode(P2_7,GPO_PP);
			break;
		}
		case PWM4P_P66:
		{
			gpio_mode(P6_6,GPO_PP);
			break;
		}
		case PWM4N_P67:
		{
			gpio_mode(P6_7,GPO_PP);
			break;
		}
		case PWM4P_P34:
		{
			gpio_mode(P3_4,GPO_PP);
			break;
		}
		case PWM4N_P33:
		{
			gpio_mode(P3_3,GPO_PP);
			break;
		}
		
		
		case PWM5_P20:
		{
			gpio_mode(P2_0,GPO_PP);
			break;
		}
		case PWM5_P17:
		{
			gpio_mode(P1_7,GPO_PP);
			break;
		}
		case PWM5_P00:
		{
			gpio_mode(P0_0,GPO_PP);
			break;
		}
		case PWM5_P74:
		{
			gpio_mode(P7_4,GPO_PP);
			break;
		}
		
		case PWM6_P21:
		{
			gpio_mode(P2_1,GPO_PP);
			break;
		}
		case PWM6_P54:
		{
			gpio_mode(P5_4,GPO_PP);
			break;
		}
		case PWM6_P01:
		{
			gpio_mode(P0_1,GPO_PP);
			break;
		}
		case PWM6_P75:
		{
			gpio_mode(P7_5,GPO_PP);
			break;
		}

		
		case PWM7_P22:
		{
			gpio_mode(P2_2,GPO_PP);
			break;
		}
		case PWM7_P33:
		{
			gpio_mode(P3_3,GPO_PP);
			break;
		}
		case PWM7_P02:
		{
			gpio_mode(P0_2,GPO_PP);
			break;
		}
		case PWM7_P76:
		{
			gpio_mode(P7_6,GPO_PP);
			break;
		}

		
		case PWM8_P23:
		{
			gpio_mode(P2_3,GPO_PP);
			break;
		}
		case PWM8_P34:
		{
			gpio_mode(P3_4,GPO_PP);
			break;
		}
		case PWM8_P03:
		{
			gpio_mode(P0_3,GPO_PP);
			break;
		}
		case PWM8_P77:
		{
			gpio_mode(P7_7,GPO_PP);
			break;
		}
		
	}
	
}
	
	
//-------------------------------------------------------------------------------------------------------------------
//  @brief      PWM初始化
//  @param      pwmch       PWM通道号及引脚
//  @param      freq        PWM频率
//  @param      duty        PWM占空比
//  @return     void
//  Sample usage:           
//							pwm_init(PWM0_P00, 100, 5000);     //初始化PWM0  使用引脚P0.0  输出PWM频率100HZ   占空比为百分之 5000/PWM_DUTY_MAX*100
//							PWM_DUTY_MAX在zf_pwm.h文件中 默认为10000
//-------------------------------------------------------------------------------------------------------------------
void pwm_init(PWMCH_enum pwmch,uint32 freq, uint16 duty)
{
	
	uint16 match_temp;
	uint16 period_temp; 
	uint16 freq_div = 0;
	
	P_SW2 |= 0x80;
	
	//GPIO需要设置为推挽输出
	pwm_set_gpio(pwmch);


	
	//分频计算，周期计算，占空比计算
	freq_div = (sys_clk / freq) >> 16;							//多少分频
	period_temp = sys_clk / freq / (freq_div + 1) - 1;			//周期
	match_temp = period_temp * ((float)duty / PWM_DUTY_MAX);	//占空比
	
	
	
	if(PWM5_P20 <= pwmch)				//PWM5-8
	{
		
		
		//通道选择，引脚选择
		PWM2_ENO |= (1 << ((2 * ((pwmch >> 4) - 4))));					//使能通道	
		PWM2_PS |= ((pwmch & 0x03) << ((2 * ((pwmch >> 4) - 4))));		//输出脚选择
		
//		// 配置通道输出使能和极性	
		(*(unsigned char volatile xdata *)(PWM2_CCER1_ADDR + (((pwmch >> 4) - 4) >> 1))) |= (1 << (((pwmch >> 4) & 0x01) * 4));
		
		//功能设置
		(*(unsigned char volatile xdata *)(PWM2_CCMR1_ADDR + ((pwmch >> 4) - 4))) |= 0x06<<4;	//设置为PWM模式1
		(*(unsigned char volatile xdata *)(PWM2_CCMR1_ADDR + ((pwmch >> 4) - 4))) |= 1<<3;		//开启PWM2_CCR1 寄存器的预装载功能
		
		//周期
		PWM2_ARR = period_temp;
		//设置预分频
		PWM2_PSCR = freq_div;
		//设置捕获值|比较值
		(*(unsigned int volatile xdata *)(PWM2_CCR1_ADDR + 2 * ((pwmch >> 4) - 4))) = match_temp;
		
		PWM2_BKR = 0x80; 	//主输出使能 相当于总开关
		PWM2_CR1 = 0x01;	//PWM开始计数
		
	}
	else
	{
		PWM1_ENO |= (1 << (pwmch & 0x01)) << ((pwmch >> 4) * 2);	//使能通道	
		PWM1_PS  |= ((pwmch & 0x07) >> 1) << ((pwmch >> 4) * 2);    //输出脚选择

		
		// 配置通道输出使能和极性
		(*(unsigned char volatile xdata *)(PWM1_CCER1_ADDR + (pwmch >> 5))) |= (1 << ((pwmch & 0x01) * 2 + ((pwmch >> 4) & 0x01) * 0x04));
			
		
		(*(unsigned char volatile xdata *)(PWM1_CCMR1_ADDR + (pwmch >> 4))) |= 0x06<<4;		//设置为PWM模式1
		(*(unsigned char volatile xdata *)(PWM1_CCMR1_ADDR + (pwmch >> 4))) |= 1<<3;		//开启PWM1_CCR1 寄存器的预装载功能
		
		//周期
		PWM1_ARR = period_temp;
		//设置预分频
		PWM1_PSCR = freq_div;
		//设置捕获值|比较值
		(*(unsigned int volatile xdata *)(PWM1_CCR1_ADDR + 2 * (pwmch >> 4))) = match_temp;
		
		PWM1_BKR = 0x80; 	// 主输出使能 相当于总开关
		PWM1_CR1 = 0x01;	//PWM开始计数
		
	}

//	P_SW2 &= 0x7F;

}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      PWM占空比设置
//  @param      pwmch       PWM通道号及引脚
//  @param      duty        PWM占空比
//  @return     void
//  Sample usage:           pwm_duty(PWM0_P00, 5000);     //初始化PWM0  使用引脚P0.0  输出PWM频率50HZ   占空比为百分之 5000/PWM_DUTY_MAX*100
//							PWM_DUTY_MAX在fsl_pwm.h文件中 默认为10000
//-------------------------------------------------------------------------------------------------------------------
void pwm_duty(PWMCH_enum pwmch, uint16 duty)
{
	uint16 match_temp;
	
//	P_SW2 |= 0x80;
	if(PWM5_P20 <= pwmch)				//PWM5-8
	{
		match_temp = (uint16)(PWM2_ARR * ((float)duty/PWM_DUTY_MAX));				//占空比
		(*(unsigned int volatile xdata *)(PWM2_CCR1_ADDR + 2 * ((pwmch >> 4) - 4))) = match_temp;
	}
	else
	{
		match_temp = (uint16)(PWM1_ARR * ((float)duty/PWM_DUTY_MAX));				//占空比
		(*(unsigned int volatile xdata *)(PWM1_CCR1_ADDR + 2 * (pwmch >> 4))) = match_temp;
	}
	

//	P_SW2 &= ~0x80;
	
}


//-------------------------------------------------------------------------------------------------------------------
//  @brief      PWM频率设置
//  @param      pwmch       PWM通道号及引脚
//  @param      freq        PWM频率
//  @param      duty        PWM占空比
//  @return     void
//  Sample usage:           pwm_freq(PWM0_P00, 50, 5000);     //修改化PWM0  使用引脚P0.0  输出PWM频率50HZ   占空比为百分之 5000/PWM_DUTY_MAX*100
//-------------------------------------------------------------------------------------------------------------------
void pwm_freq(PWMCH_enum pwmch, uint32 freq, uint16 duty)
{
	uint32 match_temp;
    uint32 period_temp; 
	uint8 freq_div = 0;
	
	freq_div = (sys_clk/freq)>>15;								//预分频值
	period_temp = sys_clk/freq/(freq_div + 1);					//周期
	match_temp = period_temp*((float)duty/PWM_DUTY_MAX);	//占空比
	
//	P_SW2 |= 0x80;
	
	
	if(PWM5_P20 <= pwmch)				//PWM5-8
	{
		//周期
		PWM2_ARR = period_temp;
		//设置预分频
		PWM2_PSCR = freq_div;
		//设置捕获值|比较值
		(*(unsigned int volatile xdata *)(PWM2_CCR1_ADDR + 2 * ((pwmch >> 4) - 4))) = match_temp;
	}
	else
	{
		//周期
		PWM1_ARR = period_temp;
		//设置预分频
		PWM1_PSCR = freq_div;
		//设置捕获值|比较值
		(*(unsigned int volatile xdata *)(PWM1_CCR1_ADDR + 2 * (pwmch >> 4))) = match_temp;
	}
	
//	P_SW2 &= ~0x80;
}


