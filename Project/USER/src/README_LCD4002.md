# LCD4002液晶屏I2C驱动使用说明

## 概述
本驱动适用于STC8H8K64单片机，使用软件I2C方式驱动基于PCF8574扩展芯片的LCD4002（40×2字符）液晶屏。

## 硬件连接
| LCD4002模块 | STC8H8K64单片机 | 说明 |
|-------------|----------------|------|
| VCC | 5V (或3.3V) | 电源正极，根据模块规格选择 |
| GND | GND | 电源负极 |
| SDA | P1.4 | I2C数据线 |
| SCL | P1.5 | I2C时钟线 |

## 配置说明

### I2C地址配置
- 默认地址：0x27
- 如需修改，请更改 `SEEKFREE_LCD4002_I2C.h` 中的 `LCD4002_I2C_ADDR` 宏定义

### I2C引脚配置
- 默认引脚：SCL-P1.5, SDA-P1.4
- 如需修改，请更改 `SEEKFREE_SOFT_I2C.h` 中的引脚宏定义：
  ```c
  #define SOFT_I2C_SCL_PIN    P15  // SCL引脚
  #define SOFT_I2C_SDA_PIN    P14  // SDA引脚
  ```

### I2C速度调整
- 如果通信不稳定，可以修改 `SEEKFREE_SOFT_I2C.h` 中的 `SOFT_I2C_DELAY_TIME` 值
- 增大该值可降低I2C速度，提高稳定性

## API接口

### 初始化函数
```c
void lcd4002_init(void);
```
- 功能：初始化LCD4002液晶屏
- 参数：无
- 返回：无
- 说明：程序开始时必须调用此函数

### 基础控制函数
```c
void lcd4002_clear(void);                    // 清屏
void lcd4002_home(void);                     // 光标回到原点
void lcd4002_backlight(uint8 state);        // 背光控制（0:关闭, 1:开启）
void lcd4002_set_cursor(uint8 col, uint8 row); // 设置光标位置（col:0-39, row:0-1）
```

### 显示函数
```c
void lcd4002_write_char(uint8 data);         // 写入单个字符
void lcd4002_write_string(char *str);       // 写入字符串
void lcd4002_write_string_at(uint8 col, uint8 row, char *str); // 在指定位置写入字符串
```

### 数值显示函数
```c
void lcd4002_write_number(int32 num);        // 写入整数
void lcd4002_write_number_at(uint8 col, uint8 row, int32 num); // 在指定位置写入整数
void lcd4002_write_float(float num, uint8 decimal_places);     // 写入浮点数
void lcd4002_write_float_at(uint8 col, uint8 row, float num, uint8 decimal_places); // 在指定位置写入浮点数
```

### 自定义字符函数
```c
void lcd4002_create_char(uint8 location, uint8 charmap[]); // 创建自定义字符（location:0-7）
void lcd4002_display_char(uint8 location);                // 显示自定义字符
```

## 使用示例

### 基本显示示例
```c
#include "headfile.h"

void main()
{
    board_init();
    
    // 初始化LCD
    lcd4002_init();
    
    // 显示文本
    lcd4002_write_string_at(0, 0, "Hello, World!");
    lcd4002_write_string_at(0, 1, "LCD4002 Test");
    
    while(1)
    {
        // 主循环
    }
}
```

### 动态数据显示示例
```c
#include "headfile.h"

void main()
{
    uint32 counter = 0;
    float temperature = 25.5;
    
    board_init();
    lcd4002_init();
    
    // 显示标题
    lcd4002_write_string_at(0, 0, "Count:");
    lcd4002_write_string_at(20, 0, "Temp:");
    
    while(1)
    {
        // 显示计数值
        lcd4002_write_number_at(6, 0, counter);
        
        // 显示温度
        lcd4002_write_float_at(25, 0, temperature, 1);
        lcd4002_write_char(0xDF); // 度符号
        lcd4002_write_char('C');
        
        counter++;
        temperature += 0.1;
        delay_ms(1000);
    }
}
```

### 自定义字符示例
```c
#include "headfile.h"

void main()
{
    // 定义心形字符点阵
    uint8 heart[8] = {
        0x00, 0x0A, 0x1F, 0x1F, 0x0E, 0x04, 0x00, 0x00
    };
    
    board_init();
    lcd4002_init();
    
    // 创建自定义字符
    lcd4002_create_char(0, heart);
    
    // 显示自定义字符
    lcd4002_write_string_at(0, 0, "I ");
    lcd4002_display_char(0);  // 显示心形
    lcd4002_write_string(" STC8H!");
    
    while(1)
    {
        // 主循环
    }
}
```

## 注意事项

1. **电源电压**：确保LCD4002模块的工作电压与单片机匹配
2. **I2C地址**：不同厂家的PCF8574可能有不同的默认地址（常见：0x27, 0x3F）
3. **引脚连接**：确保SDA、SCL引脚连接正确，建议添加上拉电阻
4. **初始化顺序**：必须先调用 `board_init()` 再调用 `lcd4002_init()`
5. **延时处理**：某些操作后建议添加适当延时，确保LCD响应完成

## 故障排除

### 显示异常或无显示
1. 检查硬件连接是否正确
2. 确认I2C地址是否正确
3. 尝试增大 `SOFT_I2C_DELAY_TIME` 值
4. 检查电源电压是否稳定

### 字符显示乱码
1. 确认字符编码是否正确
2. 检查初始化时序是否完整
3. 验证PCF8574的引脚映射是否匹配

### 背光不亮
1. 检查PCF8574的P3引脚连接
2. 确认背光控制逻辑（有些模块是低电平有效）
3. 检查背光电路是否正常

如有其他问题，请参考逐飞科技官方技术支持。 