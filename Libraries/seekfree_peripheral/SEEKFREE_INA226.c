#include "SEEKFREE_INA226.h"
#include "zf_delay.h"

// R_SHUNT is the value of the shunt resistor in Ohms
#define R_SHUNT 0.1f 

// This value is calculated as: 0.00512 / (CURRENT_LSB * R_SHUNT)
// For this driver, we'll use a CURRENT_LSB of 1mA/bit, so CAL = 0.00512 / (0.001 * 0.1) = 51.2
// We will round this to 51 and load it into the calibration register.
// This will result in a CURRENT_LSB of 0.00512 / (51 * 0.1) = 1mA/bit
static uint16 ina226_cal_value = 56;

//=================================================================================================================
// @brief    Write a 16-bit value to a register on the INA226
// @param    reg: The register to write to
// @param    value: The 16-bit value to write
//=================================================================================================================
void ina226_write_register(uint8 reg, uint16 value)
{
    uint8 buffer[2];
    buffer[0] = (value >> 8) & 0xFF;
    buffer[1] = value & 0xFF;
    soft_i2c_write_bytes(INA226_ADDRESS, reg, buffer, 2);
}

//=================================================================================================================
// @brief    Read a 16-bit value from a register on the INA226
// @param    reg: The register to read from
// @return   The 16-bit value read from the register
//=================================================================================================================
uint16 ina226_read_register(uint8 reg)
{
    uint8 buffer[2];
    soft_i2c_read_bytes(INA226_ADDRESS, reg, buffer, 2);
    return ((uint16)buffer[0] << 8) | buffer[1];
}

//=================================================================================================================
// @brief    Initialize the INA226 sensor
//=================================================================================================================
void ina226_init(void)
{
    uint16 config = INA226_CONFIG_AVG_128 |
                    INA226_CONFIG_VBUSCT_1100us |
                    INA226_CONFIG_VSHCT_1100us |
                    INA226_CONFIG_MODE_SANDBVOLT_CONTINUOUS;
    //ina226
    ina226_write_register(INA226_REG_CONFIG, config);
    ina226_write_register(INA226_REG_CALIBRATION, ina226_cal_value);
	
	
	  //ina219a
	  //ina226_write_register(0x00, 0x399F);
    //ina226_write_register(0x05, 0x1000);
}

//=================================================================================================================
// @brief    Get the current from the INA226 sensor
// @return   The current in Amperes
//=================================================================================================================
float ina226_get_current(void)
{
    int16 current_reg = (int16)ina226_read_register(INA226_REG_CURRENT);
    return (float)current_reg * 0.001f; // 1mA per LSB
}

//=================================================================================================================
// @brief    Get the bus voltage from the INA226 sensor
// @return   The bus voltage in Volts
//=================================================================================================================
float ina226_get_bus_voltage(void)
{
    uint16 bus_voltage_reg = ina226_read_register(INA226_REG_BUSVOLTAGE);
    return (float)bus_voltage_reg * 0.00125f; // 1.25mV per LSB
}

//=================================================================================================================
// @brief    Get the power from the INA226 sensor
// @return   The power in Watts
//=================================================================================================================
float ina226_get_power(void)
{
    uint16 power_reg = ina226_read_register(INA226_REG_POWER);
    return (float)power_reg * 25 * 0.001f; // 25 * current_lsb (1mA)
} 