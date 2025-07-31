#ifndef     __STC8H_H_
#define     __STC8H_H_

/////////////////////////////////////////////////

//包含本头文件后,不用另外再包含"REG51.H"

sfr         P0          =           0x80;
sbit        P00         =           P0^0;
sbit        P01         =           P0^1;
sbit        P02         =           P0^2;
sbit        P03         =           P0^3;
sbit        P04         =           P0^4;
sbit        P05         =           P0^5;
sbit        P06         =           P0^6;
sbit        P07         =           P0^7;
sfr         SP          =           0x81;
sfr         DPL         =           0x82;
sfr         DPH         =           0x83;
sfr         S4CON       =           0x84;
sfr         S4BUF       =           0x85;
sfr         PCON        =           0x87;
sfr         TCON        =           0x88;
sbit        TF1         =           TCON^7;
sbit        TR1         =           TCON^6;
sbit        TF0         =           TCON^5;
sbit        TR0         =           TCON^4;
sbit        IE1         =           TCON^3;
sbit        IT1         =           TCON^2;
sbit        IE0         =           TCON^1;
sbit        IT0         =           TCON^0;
sfr         TMOD        =           0x89;
sfr         TL0         =           0x8a;
sfr         TL1         =           0x8b;
sfr         TH0         =           0x8c;
sfr         TH1         =           0x8d;
sfr         AUXR        =           0x8e;
sfr         INTCLKO     =           0x8f;
sfr         P1          =           0x90;
sbit        P10         =           P1^0;
sbit        P11         =           P1^1;
sbit        P12         =           P1^2;
sbit        P13         =           P1^3;
sbit        P14         =           P1^4;
sbit        P15         =           P1^5;
sbit        P16         =           P1^6;
sbit        P17         =           P1^7;
sfr         P1M1        =           0x91;
sfr         P1M0        =           0x92;
sfr         P0M1        =           0x93;
sfr         P0M0        =           0x94;
sfr         P2M1        =           0x95;
sfr         P2M0        =           0x96;
sfr         SCON        =           0x98;
sbit        SM0         =           SCON^7;
sbit        SM1         =           SCON^6;
sbit        SM2         =           SCON^5;
sbit        REN         =           SCON^4;
sbit        TB8         =           SCON^3;
sbit        RB8         =           SCON^2;
sbit        TI          =           SCON^1;
sbit        RI          =           SCON^0;
sfr         SBUF        =           0x99;
sfr         S2CON       =           0x9a;
sfr         S2BUF       =           0x9b;
sfr         IRCBAND     =           0x9d;
sfr         LIRTRIM     =           0x9e;
sfr         IRTRIM      =           0x9f;
sfr         P2          =           0xa0;
sbit        P20         =           P2^0;
sbit        P21         =           P2^1;
sbit        P22         =           P2^2;
sbit        P23         =           P2^3;
sbit        P24         =           P2^4;
sbit        P25         =           P2^5;
sbit        P26         =           P2^6;
sbit        P27         =           P2^7;
sfr         P_SW1       =           0xa2;
sfr         IE          =           0xa8;
sbit        EA          =           IE^7;
sbit        ELVD        =           IE^6;
sbit        EADC        =           IE^5;
sbit        ES          =           IE^4;
sbit        ET1         =           IE^3;
sbit        EX1         =           IE^2;
sbit        ET0         =           IE^1;
sbit        EX0         =           IE^0;
sfr         SADDR       =           0xa9;
sfr         WKTCL       =           0xaa;
sfr         WKTCH       =           0xab;
sfr         S3CON       =           0xac;
sfr         S3BUF       =           0xad;
sfr         TA          =           0xae;
sfr         IE2         =           0xaf;
sfr         P3          =           0xb0;
sbit        P30         =           P3^0;
sbit        P31         =           P3^1;
sbit        P32         =           P3^2;
sbit        P33         =           P3^3;
sbit        P34         =           P3^4;
sbit        P35         =           P3^5;
sbit        P36         =           P3^6;
sbit        P37         =           P3^7;
sfr         P3M1        =           0xb1;
sfr         P3M0        =           0xb2;
sfr         P4M1        =           0xb3;
sfr         P4M0        =           0xb4;
sfr         IP2         =           0xb5;
sfr         IP2H        =           0xb6;
sfr         IPH         =           0xb7;
sfr         IP          =           0xb8;
sbit        PPCA        =           IP^7;
sbit        PLVD        =           IP^6;
sbit        PADC        =           IP^5;
sbit        PS          =           IP^4;
sbit        PT1         =           IP^3;
sbit        PX1         =           IP^2;
sbit        PT0         =           IP^1;
sbit        PX0         =           IP^0;
sfr         SADEN       =           0xb9;
sfr         P_SW2       =           0xba;
sfr         ADC_CONTR   =           0xbc;
sfr         ADC_RES     =           0xbd;
sfr         ADC_RESL    =           0xbe;
sfr         P4          =           0xc0;
sbit        P40         =           P4^0;
sbit        P41         =           P4^1;
sbit        P42         =           P4^2;
sbit        P43         =           P4^3;
sbit        P44         =           P4^4;
sbit        P45         =           P4^5;
sbit        P46         =           P4^6;
sbit        P47         =           P4^7;
sfr         WDT_CONTR   =           0xc1;
sfr         IAP_DATA    =           0xc2;
sfr         IAP_ADDRH   =           0xc3;
sfr         IAP_ADDRL   =           0xc4;
sfr         IAP_CMD     =           0xc5;
sfr         IAP_TRIG    =           0xc6;
sfr         IAP_CONTR   =           0xc7;
sfr         P5          =           0xc8;
sbit        P50         =           P5^0;
sbit        P51         =           P5^1;
sbit        P52         =           P5^2;
sbit        P53         =           P5^3;
sbit        P54         =           P5^4;
sbit        P55         =           P5^5;
sbit        P56         =           P5^6;
sbit        P57         =           P5^7;
sfr         P5M1        =           0xc9;
sfr         P5M0        =           0xca;
sfr         P6M1        =           0xcb;
sfr         P6M0        =           0xcc;
sfr         SPSTAT      =           0xcd;
sfr         SPCTL       =           0xce;
sfr         SPDAT       =           0xcf;
sfr         PSW         =           0xd0;
sbit        CY          =           PSW^7;
sbit        AC          =           PSW^6;
sbit        F0          =           PSW^5;
sbit        RS1         =           PSW^4;
sbit        RS0         =           PSW^3;
sbit        OV          =           PSW^2;
sbit        P           =           PSW^0;
sfr         T4T3M       =           0xd1;
sfr         T4H         =           0xd2;
sfr         T4L         =           0xd3;
sfr         T3H         =           0xd4;
sfr         T3L         =           0xd5;
sfr         T2H         =           0xd6;
sfr         T2L         =           0xd7;
sfr         USBCLK      =           0xdc;
sfr         ADCCFG      =           0xde;
sfr         IP3         =           0xdf;
sfr         ACC         =           0xe0;
sfr         P7M1        =           0xe1;
sfr         P7M0        =           0xe2;
sfr         DPS         =           0xe3;
sfr         DPL1        =           0xe4;
sfr         DPH1        =           0xe5;
sfr         CMPCR1      =           0xe6;
sfr         CMPCR2      =           0xe7;
sfr         P6          =           0xe8;
sbit        P60         =           P6^0;
sbit        P61         =           P6^1;
sbit        P62         =           P6^2;
sbit        P63         =           P6^3;
sbit        P64         =           P6^4;
sbit        P65         =           P6^5;
sbit        P66         =           P6^6;
sbit        P67         =           P6^7;
sfr         USBDAT      =           0xec;
sfr         IP3H        =           0xee;
sfr         AUXINTIF    =           0xef;
sfr         B           =           0xf0;
sfr         USBCON      =           0xf4;
sfr         IAP_TPS     =           0xf5;
sfr         P7          =           0xf8;
sbit        P70         =           P7^0;
sbit        P71         =           P7^1;
sbit        P72         =           P7^2;
sbit        P73         =           P7^3;
sbit        P74         =           P7^4;
sbit        P75         =           P7^5;
sbit        P76         =           P7^6;
sbit        P77         =           P7^7;
sfr         USBADR      =           0xfc;
sfr         RSTCFG      =           0xff;

//如下特殊功能寄存器位于扩展RAM区域
//访问这些寄存器,需先将P_SW2的BIT7设置为1,才可正常读写

#define     DMA_M2M_CFG        (*(unsigned char        volatile    xdata       *)0xfa00)
#define     DMA_M2M_CR         (*(unsigned char        volatile    xdata       *)0xfa01)
#define     DMA_M2M_STA        (*(unsigned char        volatile    xdata       *)0xfa02)
#define     DMA_M2M_AMT        (*(unsigned char        volatile    xdata       *)0xfa03)
#define     DMA_M2M_DONE       (*(unsigned char        volatile    xdata       *)0xfa04)
#define     DMA_M2M_TXAH       (*(unsigned char        volatile    xdata       *)0xfa05)
#define     DMA_M2M_TXAL       (*(unsigned char        volatile    xdata       *)0xfa06)
#define     DMA_M2M_RXAH       (*(unsigned char        volatile    xdata       *)0xfa07)
#define     DMA_M2M_RXAL       (*(unsigned char        volatile    xdata       *)0xfa08)



#define     CKSEL       (*(unsigned char        volatile    xdata       *)0xfe00)
#define     CLKDIV      (*(unsigned char        volatile    xdata       *)0xfe01)
#define     HIRCCR      (*(unsigned char        volatile    xdata       *)0xfe02)
#define     XOSCCR      (*(unsigned char        volatile    xdata       *)0xfe03)
#define     IRC32KCR    (*(unsigned char        volatile    xdata       *)0xfe04)
#define     MCLKOCR     (*(unsigned char        volatile    xdata       *)0xfe05)

#define     P0PU        (*(unsigned char        volatile    xdata       *)0xfe10)
#define     P1PU        (*(unsigned char        volatile    xdata       *)0xfe11)
#define     P2PU        (*(unsigned char        volatile    xdata       *)0xfe12)
#define     P3PU        (*(unsigned char        volatile    xdata       *)0xfe13)
#define     P4PU        (*(unsigned char        volatile    xdata       *)0xfe14)
#define     P5PU        (*(unsigned char        volatile    xdata       *)0xfe15)
#define     P6PU        (*(unsigned char        volatile    xdata       *)0xfe16)
#define     P7PU        (*(unsigned char        volatile    xdata       *)0xfe17)
#define     P0NCS       (*(unsigned char        volatile    xdata       *)0xfe18)
#define     P1NCS       (*(unsigned char        volatile    xdata       *)0xfe19)
#define     P2NCS       (*(unsigned char        volatile    xdata       *)0xfe1a)
#define     P3NCS       (*(unsigned char        volatile    xdata       *)0xfe1b)
#define     P4NCS       (*(unsigned char        volatile    xdata       *)0xfe1c)
#define     P5NCS       (*(unsigned char        volatile    xdata       *)0xfe1d)
#define     P6NCS       (*(unsigned char        volatile    xdata       *)0xfe1e)
#define     P7NCS       (*(unsigned char        volatile    xdata       *)0xfe1f)
#define     P0SR        (*(unsigned char        volatile    xdata       *)0xfe20)
#define     P1SR        (*(unsigned char        volatile    xdata       *)0xfe21)
#define     P2SR        (*(unsigned char        volatile    xdata       *)0xfe22)
#define     P3SR        (*(unsigned char        volatile    xdata       *)0xfe23)
#define     P4SR        (*(unsigned char        volatile    xdata       *)0xfe24)
#define     P5SR        (*(unsigned char        volatile    xdata       *)0xfe25)
#define     P6SR        (*(unsigned char        volatile    xdata       *)0xfe26)
#define     P7SR        (*(unsigned char        volatile    xdata       *)0xfe27)
#define     P0DR        (*(unsigned char        volatile    xdata       *)0xfe28)
#define     P1DR        (*(unsigned char        volatile    xdata       *)0xfe29)
#define     P2DR        (*(unsigned char        volatile    xdata       *)0xfe2a)
#define     P3DR        (*(unsigned char        volatile    xdata       *)0xfe2b)
#define     P4DR        (*(unsigned char        volatile    xdata       *)0xfe2c)
#define     P5DR        (*(unsigned char        volatile    xdata       *)0xfe2d)
#define     P6DR        (*(unsigned char        volatile    xdata       *)0xfe2e)
#define     P7DR        (*(unsigned char        volatile    xdata       *)0xfe2f)
#define     P0IE        (*(unsigned char        volatile    xdata       *)0xfe30)
#define     P1IE        (*(unsigned char        volatile    xdata       *)0xfe31)
#define     P3IE        (*(unsigned char        volatile    xdata       *)0xfe33)
#define     I2CCFG      (*(unsigned char        volatile    xdata       *)0xfe80)
#define     I2CMSCR     (*(unsigned char        volatile    xdata       *)0xfe81)
#define     I2CMSST     (*(unsigned char        volatile    xdata       *)0xfe82)
#define     I2CSLCR     (*(unsigned char        volatile    xdata       *)0xfe83)
#define     I2CSLST     (*(unsigned char        volatile    xdata       *)0xfe84)
#define     I2CSLADR    (*(unsigned char        volatile    xdata       *)0xfe85)
#define     I2CTXD      (*(unsigned char        volatile    xdata       *)0xfe86)
#define     I2CRXD      (*(unsigned char        volatile    xdata       *)0xfe87)
#define     I2CMSAUX    (*(unsigned char        volatile    xdata       *)0xfe88)
#define     TM2PS       (*(unsigned char        volatile    xdata       *)0xfea2)
#define     TM3PS       (*(unsigned char        volatile    xdata       *)0xfea3)
#define     TM4PS       (*(unsigned char        volatile    xdata       *)0xfea4)
#define     ADCTIM      (*(unsigned char        volatile    xdata       *)0xfea8)

#define     PWM1_ETRPS  (*(unsigned char volatile xdata *)0xfeb0)
#define     PWM1_ENO    (*(unsigned char volatile xdata *)0xfeb1)
#define     PWM1_PS     (*(unsigned char volatile xdata *)0xfeb2)
#define     PWM1_IOAUX  (*(unsigned char volatile xdata *)0xfeb3)
#define     PWM2_ETRPS  (*(unsigned char volatile xdata *)0xfeb4)
#define     PWM2_ENO    (*(unsigned char volatile xdata *)0xfeb5)
#define     PWM2_PS     (*(unsigned char volatile xdata *)0xfeb6)
#define     PWM2_IOAUX  (*(unsigned char volatile xdata *)0xfeb7)
#define     PWM1_CR1    (*(unsigned char volatile xdata *)0xfec0)
#define     PWM1_CR2    (*(unsigned char volatile xdata *)0xfec1)
#define     PWM1_SMCR   (*(unsigned char volatile xdata *)0xfec2)
#define     PWM1_ETR    (*(unsigned char volatile xdata *)0xfec3)
#define     PWM1_IER    (*(unsigned char volatile xdata *)0xfec4)
#define     PWM1_SR1    (*(unsigned char volatile xdata *)0xfec5)
#define     PWM1_SR2    (*(unsigned char volatile xdata *)0xfec6)
#define     PWM1_EGR    (*(unsigned char volatile xdata *)0xfec7)
#define     PWM1_CCMR1  (*(unsigned char volatile xdata *)0xfec8)
#define     PWM1_CCMR2  (*(unsigned char volatile xdata *)0xfec9)
#define     PWM1_CCMR3  (*(unsigned char volatile xdata *)0xfeca)
#define     PWM1_CCMR4  (*(unsigned char volatile xdata *)0xfecb)
#define     PWM1_CCER1  (*(unsigned char volatile xdata *)0xfecc)
#define     PWM1_CCER2  (*(unsigned char volatile xdata *)0xfecd)
#define     PWM1_CNTR   (*(unsigned int volatile xdata *)0xfece)
#define     PWM1_CNTRH  (*(unsigned char volatile xdata *)0xfece)
#define     PWM1_CNTRL  (*(unsigned char volatile xdata *)0xfecf)
#define     PWM1_PSCR   (*(unsigned int volatile xdata *)0xfed0)
#define     PWM1_PSCRH  (*(unsigned char volatile xdata *)0xfed0)
#define     PWM1_PSCRL  (*(unsigned char volatile xdata *)0xfed1)
#define     PWM1_ARR    (*(unsigned int volatile xdata *)0xfed2)
#define     PWM1_ARRH   (*(unsigned char volatile xdata *)0xfed2)
#define     PWM1_ARRL   (*(unsigned char volatile xdata *)0xfed3)
#define     PWM1_RCR    (*(unsigned char volatile xdata *)0xfed4)
#define     PWM1_CCR1   (*(unsigned int volatile xdata *)0xfed5)
#define     PWM1_CCR1H  (*(unsigned char volatile xdata *)0xfed5)
#define     PWM1_CCR1L  (*(unsigned char volatile xdata *)0xfed6)
#define     PWM1_CCR2   (*(unsigned int volatile xdata *)0xfed7)
#define     PWM1_CCR2H  (*(unsigned char volatile xdata *)0xfed7)
#define     PWM1_CCR2L  (*(unsigned char volatile xdata *)0xfed8)
#define     PWM1_CCR3   (*(unsigned int volatile xdata *)0xfed9)
#define     PWM1_CCR3H  (*(unsigned char volatile xdata *)0xfed9)
#define     PWM1_CCR3L  (*(unsigned char volatile xdata *)0xfeda)
#define     PWM1_CCR4   (*(unsigned int volatile xdata *)0xfedb)
#define     PWM1_CCR4H  (*(unsigned char volatile xdata *)0xfedb)
#define     PWM1_CCR4L  (*(unsigned char volatile xdata *)0xfedc)
#define     PWM1_BKR    (*(unsigned char volatile xdata *)0xfedd)
#define     PWM1_DTR    (*(unsigned char volatile xdata *)0xfede)
#define     PWM1_OISR   (*(unsigned char volatile xdata *)0xfedf)
#define     PWM2_CR1    (*(unsigned char volatile xdata *)0xfee0)
#define     PWM2_CR2    (*(unsigned char volatile xdata *)0xfee1)
#define     PWM2_SMCR   (*(unsigned char volatile xdata *)0xfee2)
#define     PWM2_ETR    (*(unsigned char volatile xdata *)0xfee3)
#define     PWM2_IER    (*(unsigned char volatile xdata *)0xfee4)
#define     PWM2_SR1    (*(unsigned char volatile xdata *)0xfee5)
#define     PWM2_SR2    (*(unsigned char volatile xdata *)0xfee6)
#define     PWM2_EGR    (*(unsigned char volatile xdata *)0xfee7)
#define     PWM2_CCMR1  (*(unsigned char volatile xdata *)0xfee8)
#define     PWM2_CCMR2  (*(unsigned char volatile xdata *)0xfee9)
#define     PWM2_CCMR3  (*(unsigned char volatile xdata *)0xfeea)
#define     PWM2_CCMR4  (*(unsigned char volatile xdata *)0xfeeb)
#define     PWM2_CCER1  (*(unsigned char volatile xdata *)0xfeec)
#define     PWM2_CCER2  (*(unsigned char volatile xdata *)0xfeed)
#define     PWM2_CNTR   (*(unsigned int volatile xdata *)0xfeee)
#define     PWM2_CNTRH  (*(unsigned char volatile xdata *)0xfeee)
#define     PWM2_CNTRL  (*(unsigned char volatile xdata *)0xfeef)
#define     PWM2_PSCR   (*(unsigned int volatile xdata *)0xfef0)
#define     PWM2_PSCRH  (*(unsigned char volatile xdata *)0xfef0)
#define     PWM2_PSCRL  (*(unsigned char volatile xdata *)0xfef1)
#define     PWM2_ARR    (*(unsigned int volatile xdata *)0xfef2)
#define     PWM2_ARRH   (*(unsigned char volatile xdata *)0xfef2)
#define     PWM2_ARRL   (*(unsigned char volatile xdata *)0xfef3)
#define     PWM2_RCR    (*(unsigned char volatile xdata *)0xfef4)
#define     PWM2_CCR1   (*(unsigned int volatile xdata *)0xfef5)
#define     PWM2_CCR1H  (*(unsigned char volatile xdata *)0xfef5)
#define     PWM2_CCR1L  (*(unsigned char volatile xdata *)0xfef6)
#define     PWM2_CCR2   (*(unsigned int volatile xdata *)0xfef7)
#define     PWM2_CCR2H  (*(unsigned char volatile xdata *)0xfef7)
#define     PWM2_CCR2L  (*(unsigned char volatile xdata *)0xfef8)
#define     PWM2_CCR3   (*(unsigned int volatile xdata *)0xfef9)
#define     PWM2_CCR3H  (*(unsigned char volatile xdata *)0xfef9)
#define     PWM2_CCR3L  (*(unsigned char volatile xdata *)0xfefa)
#define     PWM2_CCR4   (*(unsigned int volatile xdata *)0xfefb)
#define     PWM2_CCR4H  (*(unsigned char volatile xdata *)0xfefb)
#define     PWM2_CCR4L  (*(unsigned char volatile xdata *)0xfefc)
#define     PWM2_BKR    (*(unsigned char volatile xdata *)0xfefd)
#define     PWM2_DTR    (*(unsigned char volatile xdata *)0xfefe)
#define     PWM2_OISR   (*(unsigned char volatile xdata *)0xfeff)

/////////////////////////////////////////////////
//硬件乘除法
#define MD3U32 (*(unsigned long volatile xdata *)0xfcf0)
#define MD3U16 (*(unsigned int volatile xdata *)0xfcf0)
#define MD1U16 (*(unsigned int volatile xdata *)0xfcf2)
#define MD5U16 (*(unsigned int volatile xdata *)0xfcf4)
#define MD3 (*(unsigned char volatile xdata *)0xfcf0)
#define MD2 (*(unsigned char volatile xdata *)0xfcf1)
#define MD1 (*(unsigned char volatile xdata *)0xfcf2)
#define MD0 (*(unsigned char volatile xdata *)0xfcf3)
#define MD5 (*(unsigned char volatile xdata *)0xfcf4)
#define MD4 (*(unsigned char volatile xdata *)0xfcf5)
#define ARCON (*(unsigned char volatile xdata *)0xfcf6)
#define OPCON (*(unsigned char volatile xdata *)0xfcf7)


// 系统频率相关寄存器
sfr VRTRIM = 0xA6;
#define CLKSEL (*(unsigned char volatile xdata *)0xfe00)
#define CLKDIV (*(unsigned char volatile xdata *)0xfe01)
#define CPUIDBASE 0xfde0
#define T22M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x0b)) //22.1184MHz
#define T24M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x0c)) //24MHz
#define T27M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x0d)) //27MHz
#define T30M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x0e)) //30MHz
#define T33M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x0f)) //33.1776MHz
#define T35M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x10)) //35MHz
#define T36M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x11)) //36.864MHz
#define T40M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x12)) //40MHz
#define T44M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x13)) //44.2368MHz
#define T48M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x14)) //48MHz

#define VRT6M_ADDR 	(*(unsigned char volatile xdata *)(CPUIDBASE + 0x15)) //VRTRIM_6M
#define VRT10M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x16)) //VRTRIM_10M
#define VRT27M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x17)) //VRTRIM_27M
#define VRT44M_ADDR (*(unsigned char volatile xdata *)(CPUIDBASE + 0x18)) //VRTRIM_44M
#define CHIPID31 	(*(unsigned char volatile xdata *)(0xFDFF )) 	//STC8H8K 0x5A //TST8H8K 0x47

#endif

