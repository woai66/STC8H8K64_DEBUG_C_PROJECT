#ifndef _SEEKFREE_INA226_H
#define _SEEKFREE_INA226_H

#include "headfile.h"
#include "SEEKFREE_SOFT_I2C.h"

//-------------------------------------------------------------------------------------------------------------------
//  INA226 I2C address
//-------------------------------------------------------------------------------------------------------------------
#define INA226_ADDRESS          0x40    // A0, A1 are grounded. User stated 0x80, which is 0x40 << 1. The library uses 7-bit address.

//-------------------------------------------------------------------------------------------------------------------
//  INA226 Register Addresses
//-------------------------------------------------------------------------------------------------------------------
#define INA226_REG_CONFIG       0x00    // Configuration Register   
#define INA226_REG_SHUNTVOLTAGE 0x01    // Shunt Voltage Register
#define INA226_REG_BUSVOLTAGE   0x02    // Bus Voltage Register
#define INA226_REG_POWER        0x03    // Power Register
#define INA226_REG_CURRENT      0x04    // Current Register
#define INA226_REG_CALIBRATION  0x05    // Calibration Register
#define INA226_REG_MASKENABLE   0x06    // Mask/Enable Register
#define INA226_REG_ALERTLIMIT   0x07    // Alert Limit Register
#define INA226_REG_MANF_ID      0xFE    // Manufacturer ID Register
#define INA226_REG_DIE_ID       0xFF    // Die ID Register

// Configuration Register Bits
#define INA226_CONFIG_RESET         0x8000  // Reset Bit
#define INA226_CONFIG_AVG_1         0x0000  // 1 sample average
#define INA226_CONFIG_AVG_4         0x0200  // 4 samples average
#define INA226_CONFIG_AVG_16        0x0400  // 16 samples average
#define INA226_CONFIG_AVG_64        0x0600  // 64 samples average
#define INA226_CONFIG_AVG_128       0x0800  // 128 samples average
#define INA226_CONFIG_AVG_256       0x0A00  // 256 samples average
#define INA226_CONFIG_AVG_512       0x0C00  // 512 samples average
#define INA226_CONFIG_AVG_1024      0x0E00  // 1024 samples average
#define INA226_CONFIG_VBUSCT_140us  0x0000
#define INA226_CONFIG_VBUSCT_204us  0x0040
#define INA226_CONFIG_VBUSCT_332us  0x0080
#define INA226_CONFIG_VBUSCT_588us  0x00C0
#define INA226_CONFIG_VBUSCT_1100us 0x0100
#define INA226_CONFIG_VBUSCT_2116us 0x0140
#define INA226_CONFIG_VBUSCT_4156us 0x0180
#define INA226_CONFIG_VBUSCT_8244us 0x01C0
#define INA226_CONFIG_VSHCT_140us   0x0000
#define INA226_CONFIG_VSHCT_204us   0x0008
#define INA226_CONFIG_VSHCT_332us   0x0010
#define INA226_CONFIG_VSHCT_588us   0x0018
#define INA226_CONFIG_VSHCT_1100us  0x0020
#define INA226_CONFIG_VSHCT_2116us  0x0028
#define INA226_CONFIG_VSHCT_4156us  0x0030
#define INA226_CONFIG_VSHCT_8244us  0x0038
#define INA226_CONFIG_MODE_POWERDOWN        0x0000
#define INA226_CONFIG_MODE_SVOLT_TRIGGERED  0x0001
#define INA226_CONFIG_MODE_BVOLT_TRIGGERED  0x0002
#define INA226_CONFIG_MODE_SANDBVOLT_TRIGGERED 0x0003
#define INA226_CONFIG_MODE_ADCOFF           0x0004
#define INA226_CONFIG_MODE_SVOLT_CONTINUOUS 0x0005
#define INA226_CONFIG_MODE_BVOLT_CONTINUOUS 0x0006
#define INA226_CONFIG_MODE_SANDBVOLT_CONTINUOUS 0x0007

void ina226_init(void);
void ina226_write_register(uint8 reg, uint16 value);
uint16 ina226_read_register(uint8 reg);
float ina226_get_current(void);
float ina226_get_bus_voltage(void);
float ina226_get_power(void);


#endif 