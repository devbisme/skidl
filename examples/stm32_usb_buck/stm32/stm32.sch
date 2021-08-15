EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A1 33110 23386
encoding utf-8
Sheet 1 1
Title "Default"
Date "2021-8-15"
Rev "v0.1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr

$Sheet
S 5000 5000 1000 2000
U 6119a4e5
F0 "top.stm32f405r0" 100
F1 "top.stm32f405r0.sch" 100
$EndSheet

$Comp
L MCU_ST_STM32F4:STM32F405RGTx U1
U 1 1 6119a4e5
P 16550 11650
F 0 "U1" H 15950 13400 50 000 L CNN
   1   16550 11650
   1   0  0  -1
$EndComp

$Comp
L Device:C_Small C1
U 1 1 6119a4e5
P 15700 10550
F 0 "C1" H 15710 10620 50 000 L CNN
   1   15700 10550
   1   0  0  -1
$EndComp

$Comp
L Device:C_Small C2
U 1 1 6119a4e5
P 15450 10650
F 0 "C2" H 15460 10720 50 000 L CNN
   1   15450 10650
   1   0  0  -1
$EndComp

$Comp
L Device:D D1
U 1 1 6119a4e5
P 17250 13600
F 0 "D1" H 17250 13700 50 000 C CNN
   1   17250 13600
   1   0  0  -1
$EndComp

$Comp
L Device:R R1
U 1 1 6119a4e5
P 17400 11700
F 0 "R1" V 17480 11700 50 000 C CNN
   1   17400 11700
   1   0  0  -1
$EndComp

Wire Wire Line
	17400 11850 17100 13600

Wire Wire Line
	15850 10450 15700 10450

Wire Wire Line
	15850 10550 15450 10550

Wire Wire Line
	17250 11550 17400 11550

Text Notes 15837 9650 0    100  ~ 20
stm32f405r0
Wire Notes Line
	15250 9450 15250 13800
Wire Notes Line
	15250 13800 17600 13800
Wire Notes Line
	17600 13800 17600 9450
Wire Notes Line
	17600 9450 15250 9450

$EndSCHEMATC
