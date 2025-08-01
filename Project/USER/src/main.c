/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2020,逐飞科技
 * All rights reserved.
 * 技术讨论QQ群：一群：179029047(已满)  二群：244861897(已满)  三群：824575535
 *
 * 以下所有内容版权均属逐飞科技所有，未经允许不得用于商业用途，
 * 欢迎各位使用并传播本程序，修改内容时必须保留逐飞科技的版权声明。
 *
 * @file       		main
 * @company	   		成都逐飞科技有限公司
 * @author     		逐飞科技(QQ790875685)
 * @version    		查看doc内version文件 版本说明
 * @Software 		MDK FOR C51 V9.60
 * @Target core		STC8H8K64S4
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2020-06-01
 ********************************************************************************************************************/

#include "headfile.h"

/*
 * 系统频率，可查看board.h中的 FOSC 宏定义修改。
 * board.h文件中FOSC的值设置为0,则程序自动设置系统频率为44.2368MHZ
 * 在board_init中,已经将P54引脚设置为复位
 * 如果需要使用P54引脚,可以在board.c文件中的board_init()函数中删除SET_P54_RESRT即可
 */

/*
 * LCD4002液晶屏连接说明：
 * ====================================
 * LCD4002模块 -----> STC8H8K64单片机
 * ====================================
 * VCC        -----> 5V (或3.3V，根据模块电压)
 * GND        -----> GND
 * SDA        -----> P14 (软件I2C数据线)
 * SCL        -----> P15 (软件I2C时钟线)
 * ====================================
 * 
 * 注意事项：
 * 1. 确保LCD4002模块的I2C地址为0x27（默认地址）
 * 2. 如果地址不同，请修改SEEKFREE_LCD4002_I2C.h中的LCD4002_I2C_ADDR定义
 * 3. 如果需要修改I2C引脚，请修改SEEKFREE_SOFT_I2C.h中的引脚定义
 */

#define USE_INA219

void main()
{
    char text_buffer[20];
    float current;
	float vol;
	float power;
	float power_get;
    
    board_init(); // 初始化内部寄存器，勿删除此句代码。

    // 初始化LCD4002液晶屏
    lcd4002_init();

    // 初始化电流传感器
#if defined(USE_INA226)
    ina226_init();
#elif defined(USE_INA219)
    ina219_init();
#endif
    // 延时一下确保初始化完成
    delay_ms(100);

    // 显示欢迎信息
#if defined(USE_INA226)
    lcd4002_write_string_at(0, 0, "INA226 Test");
#elif defined(USE_INA219)
    lcd4002_write_string_at(0, 0, "INA219 Test");
#endif

    while (1)
    {
#if defined(USE_INA226)
        current = ina226_get_current();
		//电流矫正系数
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
        // 将电流值格式化为字符串
        sprintf(text_buffer, "I: %.3fA, V: %.3fV, P: %.3fW", current, vol, power);
        lcd4002_write_string_at(0, 0, text_buffer);
		
		
		//sprintf(text_buffer, "P_GET: %.3fW", power_get);
		//lcd4002_write_string_at(0, 1, text_buffer);

        delay_ms(10); // 每500ms刷新一次
    }
}
