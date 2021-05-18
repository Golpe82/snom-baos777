/* SPDX-License-Identifier: MIT */
#ifndef __MAIN_EXTERN_H
#define __MAIN_EXTERN_H

#include <stdlib.h>

#ifdef __cplusplus
 extern "C" {
#endif

#if defined(STM32L4)
	#include "stm32l4xx.h"
	#include "stm32l4xx_hal.h"
#else
	#error Platform not supported
#endif

extern UART_HandleTypeDef* G_hUart;
extern uint8_t G_u8_UartRxPayload[1];

#ifdef __cplusplus
 }
#endif

#endif /* __MAIN_EXTERN_H */
