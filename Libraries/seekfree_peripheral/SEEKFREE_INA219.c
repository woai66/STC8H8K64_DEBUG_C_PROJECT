#include "SEEKFREE_INA219.h"
#include "zf_delay.h"

// R_SHUNT 是分流电阻的阻值，单位为欧姆
#define R_SHUNT 0.1f 

// 校准值计算:
// Cal = 0.04096 / (Current_LSB * R_SHUNT)
// 我们期望 Current_LSB 为 1mA/bit, 但为了获得更好的分辨率, 我们选择一个不同的值。
// Datasheet 建议最大预期电流为 3.2A 时，选择 Current_LSB 为 100uA (0.0001A)。
// Cal = 0.04096 / (0.0001 * 0.1) = 4096
// Power LSB = 20 * Current_LSB = 2mW
static uint16 ina219_cal_value = 4096;
static float ina219_current_lsb = 0.0001f; // 0.1mA per bit
static float ina219_power_lsb = 0.002f;    // 2mW per bit


//=================================================================================================================
// @brief    向INA219寄存器写一个16位的值
// @param    reg: 要写入的寄存器
// @param    value: 要写入的16位值
//=================================================================================================================
void ina219_write_register(uint8 reg, uint16 value)
{
    uint8 buffer[2];
    buffer[0] = (value >> 8) & 0xFF;
    buffer[1] = value & 0xFF;
    soft_i2c_write_bytes(INA219_ADDRESS, reg, buffer, 2);
}

//=================================================================================================================
// @brief    从INA219寄存器读一个16位的值
// @param    reg: 要读取的寄存器
// @return   从寄存器读取的16位值
//=================================================================================================================
uint16 ina219_read_register(uint8 reg)
{
    uint8 buffer[2];
    soft_i2c_read_bytes(INA219_ADDRESS, reg, buffer, 2);
    return ((uint16)buffer[0] << 8) | buffer[1];
}

//=================================================================================================================
// @brief    初始化INA219传感器
//=================================================================================================================
void ina219_init(void)
{
    uint16 config = INA219_CONFIG_BVOLTAGERANGE_32V |
                    INA219_CONFIG_GAIN_8_320MV |
                    INA219_CONFIG_BADCRES_12BIT |
                    INA219_CONFIG_SADCRES_12BIT_128S_69MS |
                    INA219_CONFIG_MODE_SANDBVOLT_CONTINUOUS;
    
    ina219_write_register(INA219_REG_CONFIG, config);
    ina219_write_register(INA219_REG_CALIBRATION, ina219_cal_value);
}

//=================================================================================================================
// @brief    从INA219传感器获取总线电压
// @return   总线电压（伏特）
//=================================================================================================================
float ina219_get_bus_voltage(void)
{
    uint16 bus_voltage_reg = ina219_read_register(INA219_REG_BUSVOLTAGE);
    // 右移3位，然后乘以4mV/LSB
    return (float)(bus_voltage_reg >> 3) * 0.004f;
}

//=================================================================================================================
// @brief    从INA219传感器获取电流
// @return   电流（安培）
//=================================================================================================================
float ina219_get_current(void)
{
    int16 current_reg = (int16)ina219_read_register(INA219_REG_CURRENT);
    return (float)current_reg * ina219_current_lsb;
}

//=================================================================================================================
// @brief    从INA219传感器获取功率
// @return   功率（瓦特）
//=================================================================================================================
float ina219_get_power(void)
{
    uint16 power_reg = ina219_read_register(INA219_REG_POWER);
    return (float)power_reg * ina219_power_lsb;
} 