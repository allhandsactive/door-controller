EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "Door Controller"
Date ""
Rev "1"
Comp "All Hands Active"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 "Marion Anderson"
$EndDescr
$Comp
L project:lolinv3 U?
U 1 1 625B736B
P 5850 3350
F 0 "U?" H 6200 3575 50  0000 C CNN
F 1 "lolinv3" H 6200 3484 50  0000 C CNN
F 2 "project:lolinv3" H 6250 3450 50  0001 C CNN
F 3 "" H 6250 3450 50  0001 C CNN
	1    5850 3350
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x04_Male J?
U 1 1 625B8421
P 5350 3450
F 0 "J?" H 5458 3731 50  0000 C CNN
F 1 "Conn_01x04_Male" H 5458 3640 50  0000 C CNN
F 2 "" H 5350 3450 50  0001 C CNN
F 3 "~" H 5350 3450 50  0001 C CNN
	1    5350 3450
	1    0    0    -1  
$EndComp
Wire Wire Line
	5550 3350 5850 3350
Wire Wire Line
	5550 3450 5850 3450
Wire Wire Line
	5550 3550 5850 3550
Wire Wire Line
	5550 3650 5850 3650
Wire Wire Line
	4250 3800 4200 3800
Wire Wire Line
	4250 3800 4250 3900
Wire Wire Line
	4250 4100 4200 4100
Wire Wire Line
	4200 4000 4250 4000
Connection ~ 4250 4000
Wire Wire Line
	4250 4000 4250 4100
Wire Wire Line
	4200 3900 4250 3900
Connection ~ 4250 3900
Wire Wire Line
	4250 3900 4250 3950
Wire Wire Line
	4250 3950 4300 3950
Connection ~ 4250 3950
Wire Wire Line
	4250 3950 4250 4000
$Comp
L power:+3V3 #PWR?
U 1 1 625BA731
P 4300 3950
F 0 "#PWR?" H 4300 3800 50  0001 C CNN
F 1 "+3V3" V 4315 4078 50  0000 L CNN
F 2 "" H 4300 3950 50  0001 C CNN
F 3 "" H 4300 3950 50  0001 C CNN
	1    4300 3950
	0    1    1    0   
$EndComp
Wire Wire Line
	4250 4400 4200 4400
Wire Wire Line
	4250 4400 4250 4500
Wire Wire Line
	4250 4700 4200 4700
Wire Wire Line
	4200 4600 4250 4600
Connection ~ 4250 4600
Wire Wire Line
	4250 4600 4250 4700
Wire Wire Line
	4200 4500 4250 4500
Connection ~ 4250 4500
Wire Wire Line
	4250 4500 4250 4550
Wire Wire Line
	4250 4550 4300 4550
Connection ~ 4250 4550
Wire Wire Line
	4250 4550 4250 4600
$Comp
L power:GND #PWR?
U 1 1 625BB911
P 4300 4550
F 0 "#PWR?" H 4300 4300 50  0001 C CNN
F 1 "GND" V 4305 4422 50  0000 R CNN
F 2 "" H 4300 4550 50  0001 C CNN
F 3 "" H 4300 4550 50  0001 C CNN
	1    4300 4550
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Screw_Terminal_01x09 J?
U 1 1 625C53A6
P 5400 4350
F 0 "J?" H 5318 3725 50  0000 C CNN
F 1 "Screw_Terminal_01x09" H 5318 3816 50  0000 C CNN
F 2 "" H 5400 4350 50  0001 C CNN
F 3 "~" H 5400 4350 50  0001 C CNN
	1    5400 4350
	-1   0    0    1   
$EndComp
Wire Wire Line
	5850 4050 5800 4050
Wire Wire Line
	5800 4050 5800 4250
Wire Wire Line
	5750 4150 5750 3950
Wire Wire Line
	5750 3950 5850 3950
Wire Wire Line
	5850 3850 5700 3850
Wire Wire Line
	5700 3850 5700 4050
Wire Wire Line
	5600 3950 5650 3950
Wire Wire Line
	5650 3950 5650 3750
Wire Wire Line
	5650 3750 5850 3750
Wire Wire Line
	5600 4050 5700 4050
Wire Wire Line
	5600 4150 5750 4150
Wire Wire Line
	5600 4250 5800 4250
Wire Wire Line
	5600 4350 5850 4350
Wire Wire Line
	5600 4450 5850 4450
Wire Wire Line
	5600 4550 5850 4550
Wire Wire Line
	5600 4650 5850 4650
Wire Wire Line
	5600 4750 5850 4750
$Comp
L Connector:Screw_Terminal_01x04 J?
U 1 1 625CF9A8
P 4000 4000
F 0 "J?" H 3918 3575 50  0000 C CNN
F 1 "Screw_Terminal_01x04" H 3918 3666 50  0000 C CNN
F 2 "" H 4000 4000 50  0001 C CNN
F 3 "~" H 4000 4000 50  0001 C CNN
	1    4000 4000
	-1   0    0    1   
$EndComp
$Comp
L Connector:Screw_Terminal_01x04 J?
U 1 1 625D2B7B
P 4000 4600
F 0 "J?" H 3918 4175 50  0000 C CNN
F 1 "Screw_Terminal_01x04" H 3918 4266 50  0000 C CNN
F 2 "" H 4000 4600 50  0001 C CNN
F 3 "~" H 4000 4600 50  0001 C CNN
	1    4000 4600
	-1   0    0    1   
$EndComp
$Comp
L Connector:Screw_Terminal_01x09 J?
U 1 1 625D8F0E
P 7150 4350
F 0 "J?" H 7068 3725 50  0000 C CNN
F 1 "Screw_Terminal_01x09" H 7068 3816 50  0000 C CNN
F 2 "" H 7150 4350 50  0001 C CNN
F 3 "~" H 7150 4350 50  0001 C CNN
	1    7150 4350
	1    0    0    1   
$EndComp
Wire Wire Line
	6550 3950 6950 3950
Wire Wire Line
	6550 4050 6950 4050
Wire Wire Line
	6550 4150 6950 4150
Wire Wire Line
	6550 4250 6950 4250
Wire Wire Line
	6550 4350 6950 4350
Wire Wire Line
	6550 4450 6950 4450
Wire Wire Line
	6550 4750 6950 4750
$EndSCHEMATC
