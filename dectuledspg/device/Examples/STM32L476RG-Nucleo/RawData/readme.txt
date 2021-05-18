RawData readme file
===================

Copyright © 2018 DSP GROUP, INC
@file		RawData\readme.txt
@version 	V1.0.0

This is a Single threaded application example of MCU software of device sending raw data with UART Rx interrupt without Operation System.

Description
-----------
This directory contains a set of source files that implements a simple Voice Call application. This application provides following MCU functional:
 - send raw FUN message
 
User can press the button on stm32 device to do this action: 
 - send raw FUN message
 
******************************************************************************

Directory contents
------------------
  - RawData/Inc/main.h 							    Header for main.c
  - RawData/Inc/main_extern.h 					    Header for main.c
  - RawData/Src/AppExample.c 					    Logic to work with button
  - RawData/Src/main.c 							    Main program file, initialize GPIO and SysClock, then runs function from AppExample
 
  Support files
  -------------
  - Support/stm32l4xx_hal_conf.h 				    Library Configuration file
  - Support/stm32l4xx_it.h 						    Header for stm32l4xx_it.c 
  - Support/CmndLib_UserImpl.c   				    implementation of some os functions
  - Support/CmndLib_UserImpl_StringUtil.c   		implementation for safe string processing functions
  - Support/startup_stm32l476xx.s 	                ac6 board startup file
  - Support/stm32l4xx_hal_msp.c  				    stm32lXxx specific hardware HAL code
  - Support/stm32l4xx_it.c 						    STM32lXxx Interrupt 
  - Support/system_stm32l4xx.c 					    Peripheral Access Layer System Source File
 
 
Hardware and Software environment
---------------------------------
  - This example runs on NUCLEO-L476RG device.
  - This application has been tested with STMicroelectronics NUCLEO-L476RG Rev C
  - STM32LXxx-Nucleo Set-up    
  - Connect the Nucleo board to your PC with a USB cable type A to mini-B 
    to ST-LINK connector (CN1 / CN7 on B-L072Z-LRWAN1).
  - Please ensure that the ST-LINK connector CN2 (CN8 on B-L072Z-LRWAN1) jumpers are fitted.

How to use it ?
---------------
In order to make the program work, you must do the following :
  - Open your preferred toolchain 
  - Rebuild all files and load your image into target memory
  - Run the example
  - Install dhan shield to STM32L4 (must already be registered to a hub before)
  - Press button to send raw FUN message
  