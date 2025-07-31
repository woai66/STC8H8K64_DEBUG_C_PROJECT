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
 ********************************************************************************************************************/

#include "SEEKFREE_SOFT_I2C.h"
#include "zf_delay.h"

// I2C引脚操作宏定义
#define SCL_HIGH()    SOFT_I2C_SCL_PIN = 1
#define SCL_LOW()     SOFT_I2C_SCL_PIN = 0
#define SDA_HIGH()    SOFT_I2C_SDA_PIN = 1
#define SDA_LOW()     SOFT_I2C_SDA_PIN = 0
#define SDA_READ()    SOFT_I2C_SDA_PIN

//-------------------------------------------------------------------------------------------------------------------
//  @brief      软件I2C延时函数
//  @return     void
//  @since      v1.0
//  Sample usage:
//-------------------------------------------------------------------------------------------------------------------
static void soft_i2c_delay(void)
{
    uint8 i = SOFT_I2C_DELAY_TIME;
    while(i--);
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      软件I2C初始化
//  @return     void
//  @since      v1.0
//  Sample usage:               soft_i2c_init();
//-------------------------------------------------------------------------------------------------------------------
void soft_i2c_init(void)
{
    // 设置引脚为准双向口模式，带弱上拉
    gpio_mode(P1_5, GPIO);  // SCL
    gpio_mode(P1_4, GPIO);  // SDA
    gpio_pull_set(P1_5, PULLUP);
    gpio_pull_set(P1_4, PULLUP);
    
    // 初始化引脚状态
    SCL_HIGH();
    SDA_HIGH();
    soft_i2c_delay();
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      I2C起始信号
//  @return     void
//  @since      v1.0
//  Sample usage:               内部调用
//-------------------------------------------------------------------------------------------------------------------
void soft_i2c_start(void)
{
    SCL_HIGH();
    SDA_HIGH();
    soft_i2c_delay();
    SDA_LOW();         // 在SCL高电平期间，SDA由高变低，产生起始信号
    soft_i2c_delay();
    SCL_LOW();
    soft_i2c_delay();
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      I2C停止信号
//  @return     void
//  @since      v1.0
//  Sample usage:               内部调用
//-------------------------------------------------------------------------------------------------------------------
void soft_i2c_stop(void)
{
    SCL_LOW();
    SDA_LOW();
    soft_i2c_delay();
    SCL_HIGH();
    soft_i2c_delay();
    SDA_HIGH();        // 在SCL高电平期间，SDA由低变高，产生停止信号
    soft_i2c_delay();
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      I2C发送应答信号
//  @param      ack             应答信号 SOFT_I2C_ACK:应答 SOFT_I2C_NACK:非应答
//  @return     void
//  @since      v1.0
//  Sample usage:               内部调用
//-------------------------------------------------------------------------------------------------------------------
void soft_i2c_send_ack(uint8 ack)
{
    SCL_LOW();
    soft_i2c_delay();
    if(ack == SOFT_I2C_ACK)
        SDA_LOW();     // 发送应答信号
    else
        SDA_HIGH();    // 发送非应答信号
    soft_i2c_delay();
    SCL_HIGH();
    soft_i2c_delay();
    SCL_LOW();
    soft_i2c_delay();
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      I2C等待应答信号
//  @return     uint8           SOFT_I2C_ACK:收到应答 SOFT_I2C_NACK:未收到应答
//  @since      v1.0
//  Sample usage:               内部调用
//-------------------------------------------------------------------------------------------------------------------
uint8 soft_i2c_wait_ack(void)
{
    uint8 timeout = 0;
    
    SCL_LOW();
    SDA_HIGH();        // 释放SDA线
    soft_i2c_delay();
    SCL_HIGH();
    soft_i2c_delay();
    
    while(SDA_READ())  // 等待应答信号
    {
        timeout++;
        if(timeout > 100)  // 超时处理
        {
            soft_i2c_stop();
            return SOFT_I2C_NACK;
        }
        soft_i2c_delay();
    }
    
    SCL_LOW();
    soft_i2c_delay();
    return SOFT_I2C_ACK;
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      I2C发送一个字节
//  @param      dat            要发送的数据
//  @return     void
//  @since      v1.0
//  Sample usage:               内部调用
//-------------------------------------------------------------------------------------------------------------------
void soft_i2c_send_byte(uint8 dat)
{
    uint8 i;
    
    SCL_LOW();
    for(i = 0; i < 8; i++)
    {
        if(dat & 0x80)
            SDA_HIGH();
        else
            SDA_LOW();
        
        dat <<= 1;
        soft_i2c_delay();
        SCL_HIGH();
        soft_i2c_delay();
        SCL_LOW();
        soft_i2c_delay();
    }
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      I2C读取一个字节
//  @param      ack             应答信号 SOFT_I2C_ACK:应答 SOFT_I2C_NACK:非应答
//  @return     uint8           读取到的数据
//  @since      v1.0
//  Sample usage:               内部调用
//-------------------------------------------------------------------------------------------------------------------
uint8 soft_i2c_read_byte(uint8 ack)
{
    uint8 i;
    uint8 dat = 0;
    
    SDA_HIGH();        // 释放SDA线
    for(i = 0; i < 8; i++)
    {
        SCL_LOW();
        soft_i2c_delay();
        SCL_HIGH();
        soft_i2c_delay();
        dat <<= 1;
        if(SDA_READ())
            dat |= 0x01;
    }
    
    SCL_LOW();
    soft_i2c_send_ack(ack);
    return dat;
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      I2C写寄存器
//  @param      dev_addr        设备地址(7位地址)
//  @param      reg_addr        寄存器地址
//  @param      dat            要写入的数据
//  @return     uint8           SOFT_I2C_SUCCESS:成功 SOFT_I2C_FAIL:失败
//  @since      v1.0
//  Sample usage:               soft_i2c_write_reg(0x27, 0x00, 0xFF);
//-------------------------------------------------------------------------------------------------------------------
uint8 soft_i2c_write_reg(uint8 dev_addr, uint8 reg_addr, uint8 dat)
{
    soft_i2c_start();
    
    // 发送设备地址+写位
    soft_i2c_send_byte((dev_addr << 1) | 0x00);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return SOFT_I2C_FAIL;
    
    // 发送寄存器地址
    soft_i2c_send_byte(reg_addr);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return SOFT_I2C_FAIL;
    
    // 发送数据
    soft_i2c_send_byte(dat);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return SOFT_I2C_FAIL;
    
    soft_i2c_stop();
    return SOFT_I2C_SUCCESS;
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      I2C读寄存器
//  @param      dev_addr        设备地址(7位地址)
//  @param      reg_addr        寄存器地址
//  @return     uint8           读取到的数据
//  @since      v1.0
//  Sample usage:               uint8 dat = soft_i2c_read_reg(0x27, 0x00);
//-------------------------------------------------------------------------------------------------------------------
uint8 soft_i2c_read_reg(uint8 dev_addr, uint8 reg_addr)
{
    uint8 dat;
    
    soft_i2c_start();
    
    // 发送设备地址+写位
    soft_i2c_send_byte((dev_addr << 1) | 0x00);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return 0;
    
    // 发送寄存器地址
    soft_i2c_send_byte(reg_addr);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return 0;
    
    // 重新开始
    soft_i2c_start();
    
    // 发送设备地址+读位
    soft_i2c_send_byte((dev_addr << 1) | 0x01);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return 0;
    
    // 读取数据
    dat = soft_i2c_read_byte(SOFT_I2C_NACK);
    
    soft_i2c_stop();
    return dat;
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      I2C写多个字节
//  @param      dev_addr        设备地址(7位地址)
//  @param      reg_addr        寄存器地址
//  @param      dat            要写入的数据缓冲区
//  @param      len             数据长度
//  @return     uint8           SOFT_I2C_SUCCESS:成功 SOFT_I2C_FAIL:失败
//  @since      v1.0
//  Sample usage:               soft_i2c_write_bytes(0x27, 0x00, buffer, 4);
//-------------------------------------------------------------------------------------------------------------------
uint8 soft_i2c_write_bytes(uint8 dev_addr, uint8 reg_addr, uint8 *dat, uint8 len)
{
    uint8 i;
    
    soft_i2c_start();
    
    // 发送设备地址+写位
    soft_i2c_send_byte((dev_addr << 1) | 0x00);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return SOFT_I2C_FAIL;
    
    // 发送寄存器地址
    soft_i2c_send_byte(reg_addr);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return SOFT_I2C_FAIL;
    
    // 发送数据
    for(i = 0; i < len; i++)
    {
        soft_i2c_send_byte(dat[i]);
        if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
            return SOFT_I2C_FAIL;
    }
    
    soft_i2c_stop();
    return SOFT_I2C_SUCCESS;
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      I2C读多个字节
//  @param      dev_addr        设备地址(7位地址)
//  @param      reg_addr        寄存器地址
//  @param      dat            读取数据存储缓冲区
//  @param      len             读取数据长度
//  @return     uint8           SOFT_I2C_SUCCESS:成功 SOFT_I2C_FAIL:失败
//  @since      v1.0
//  Sample usage:               soft_i2c_read_bytes(0x27, 0x00, buffer, 4);
//-------------------------------------------------------------------------------------------------------------------
uint8 soft_i2c_read_bytes(uint8 dev_addr, uint8 reg_addr, uint8 *dat, uint8 len)
{
    uint8 i;
    
    soft_i2c_start();
    
    // 发送设备地址+写位
    soft_i2c_send_byte((dev_addr << 1) | 0x00);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return SOFT_I2C_FAIL;
    
    // 发送寄存器地址
    soft_i2c_send_byte(reg_addr);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return SOFT_I2C_FAIL;
    
    // 重新开始
    soft_i2c_start();
    
    // 发送设备地址+读位
    soft_i2c_send_byte((dev_addr << 1) | 0x01);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return SOFT_I2C_FAIL;
    
    // 读取数据
    for(i = 0; i < len; i++)
    {
        if(i == (len - 1))
            dat[i] = soft_i2c_read_byte(SOFT_I2C_NACK);  // 最后一个字节发送NACK
        else
            dat[i] = soft_i2c_read_byte(SOFT_I2C_ACK);   // 其他字节发送ACK
    }
    
    soft_i2c_stop();
    return SOFT_I2C_SUCCESS;
}

//-------------------------------------------------------------------------------------------------------------------
//  @brief      I2C直接写字节（用于PCF8574等设备）
//  @param      dev_addr        设备地址(7位地址)
//  @param      dat            要写入的数据
//  @return     uint8           SOFT_I2C_SUCCESS:成功 SOFT_I2C_FAIL:失败
//  @since      v1.0
//  Sample usage:               soft_i2c_write_byte_direct(0x27, 0xFF);
//-------------------------------------------------------------------------------------------------------------------
uint8 soft_i2c_write_byte_direct(uint8 dev_addr, uint8 dat)
{
    soft_i2c_start();
    
    // 发送设备地址+写位
    soft_i2c_send_byte((dev_addr << 1) | 0x00);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return SOFT_I2C_FAIL;
    
    // 发送数据
    soft_i2c_send_byte(dat);
    if(soft_i2c_wait_ack() == SOFT_I2C_NACK)
        return SOFT_I2C_FAIL;
    
    soft_i2c_stop();
    return SOFT_I2C_SUCCESS;
} 