/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2020,��ɿƼ�
 * All rights reserved.
 * ��������QQȺ��һȺ��179029047(����)  ��Ⱥ��244861897(����)  ��Ⱥ��824575535
 *
 * �����������ݰ�Ȩ������ɿƼ����У�δ��������������ҵ��;��
 * ��ӭ��λʹ�ò������������޸�����ʱ���뱣����ɿƼ��İ�Ȩ������
 *
 * @file       		main
 * @company	   		�ɶ���ɿƼ����޹�˾
 * @author     		��ɿƼ�(QQ790875685)
 * @version    		�鿴doc��version�ļ� �汾˵��
 * @Software 		MDK FOR C51 V9.60
 * @Target core		STC8H8K64S4
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2020-06-01
 ********************************************************************************************************************/

#include "headfile.h"

/*
 * ϵͳƵ�ʣ��ɲ鿴board.h�е� FOSC �궨���޸ġ�
 * board.h�ļ���FOSC��ֵ����Ϊ0,������Զ�����ϵͳƵ��Ϊ44.2368MHZ
 * ��board_init��,�Ѿ���P54��������Ϊ��λ
 * �����Ҫʹ��P54����,������board.c�ļ��е�board_init()������ɾ��SET_P54_RESRT����
 */

/*
 * LCD4002Һ��������˵����
 * ====================================
 * LCD4002ģ�� -----> STC8H8K64��Ƭ��
 * ====================================
 * VCC        -----> 5V (��3.3V������ģ���ѹ)
 * GND        -----> GND
 * SDA        -----> P14 (���I2C������)
 * SCL        -----> P15 (���I2Cʱ����)
 * ====================================
 * 
 * ע�����
 * 1. ȷ��LCD4002ģ���I2C��ַΪ0x27��Ĭ�ϵ�ַ��
 * 2. �����ַ��ͬ�����޸�SEEKFREE_LCD4002_I2C.h�е�LCD4002_I2C_ADDR����
 * 3. �����Ҫ�޸�I2C���ţ����޸�SEEKFREE_SOFT_I2C.h�е����Ŷ���
 */

#define USE_INA219

void main()
{
    char text_buffer[20];
    float current;
	float vol;
	float power;
	float power_get;
    
    board_init(); // ��ʼ���ڲ��Ĵ�������ɾ���˾���롣

    // ��ʼ��LCD4002Һ����
    lcd4002_init();

    // ��ʼ������������
#if defined(USE_INA226)
    ina226_init();
#elif defined(USE_INA219)
    ina219_init();
#endif
    // ��ʱһ��ȷ����ʼ�����
    delay_ms(100);

    // ��ʾ��ӭ��Ϣ
#if defined(USE_INA226)
    lcd4002_write_string_at(0, 0, "INA226 Test");
#elif defined(USE_INA219)
    lcd4002_write_string_at(0, 0, "INA219 Test");
#endif

    while (1)
    {
#if defined(USE_INA226)
        current = ina226_get_current();
		//��������ϵ��
		current /=1.11f;
        vol = ina226_get_bus_voltage();
		power = current * vol;
		power_get = ina226_get_power();
#elif defined(USE_INA219)
        current = ina219_get_current();
        vol = ina219_get_bus_voltage();
        power = current * vol;
        power_get = ina219_get_power();
#endif
        // ������ֵ��ʽ��Ϊ�ַ���
        sprintf(text_buffer, "I: %.3fA, V: %.3fV, P: %.3fW", current, vol, power);
        lcd4002_write_string_at(0, 0, text_buffer);
		
		
		//sprintf(text_buffer, "P_GET: %.3fW", power_get);
		//lcd4002_write_string_at(0, 1, text_buffer);

        delay_ms(10); // ÿ500msˢ��һ��
    }
}
