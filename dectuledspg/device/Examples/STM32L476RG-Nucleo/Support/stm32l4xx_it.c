/**
  ******************************************************************************
  * @file    stm32l4xx_it.c
  * @brief   Interrupt Service Routines.
  ******************************************************************************
  *
  * COPYRIGHT(c) 2017 STMicroelectronics
  *
  * Redistribution and use in source and binary forms, with or without modification,
  * are permitted provided that the following conditions are met:
  *   1. Redistributions of source code must retain the above copyright notice,
  *      this list of conditions and the following disclaimer.
  *   2. Redistributions in binary form must reproduce the above copyright notice,
  *      this list of conditions and the following disclaimer in the documentation
  *      and/or other materials provided with the distribution.
  *   3. Neither the name of STMicroelectronics nor the names of its contributors
  *      may be used to endorse or promote products derived from this software
  *      without specific prior written permission.
  *
  * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
  * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
  * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
  * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
  * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
  * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  *
  ******************************************************************************
  */
/* Includes ------------------------------------------------------------------*/

#include <string.h>
#include "stm32l4xx_it.h"
#include "main_extern.h"

/* USER CODE BEGIN 0 */
//#include "IoPortUart.h"


/* USER CODE END 0 */

/* External variables --------------------------------------------------------*/


/******************************************************************************/
/*            Cortex-M4 Processor Interruption and Exception Handlers         */ 
/******************************************************************************/

/**
* @brief This function handles System tick timer.
*/
void SysTick_Handler(void)
{
  /* USER CODE BEGIN SysTick_IRQn 0 */

  /* USER CODE END SysTick_IRQn 0 */
  HAL_IncTick();
  /* USER CODE BEGIN SysTick_IRQn 1 */

  /* USER CODE END SysTick_IRQn 1 */
}

/******************************************************************************/
/* STM32L4xx Peripheral Interrupt Handlers                                    */
/* Add here the Interrupt Handlers for the used peripherals.                  */
/* For the available peripheral interrupt handler names,                      */
/* please refer to the startup file (startup_stm32l4xx.s).                    */
/******************************************************************************/

/**
* @brief This function handles USART1 global interrupt.
*/
void USART1_IRQHandler(void)
{
  /* USER CODE BEGIN USART2_IRQn 0 */
  HAL_UART_IRQHandler( G_hUart );
  /* USER CODE END USART2_IRQn 0 */

  /* USER CODE BEGIN USART2_IRQn 1 */
  /* USER CODE END USART2_IRQn 1 */
}

/* USER CODE BEGIN 1 */
void HAL_UART_ErrorCallback	( UART_HandleTypeDef * huart )	
{
	//HAL_UART_ErrorTypeDef:
	//HAL_UART_ERROR_NONE      = 0x00,    /*!< No error            */
	//HAL_UART_ERROR_PE        = 0x01,    /*!< Parity error        */
	//HAL_UART_ERROR_NE        = 0x02,    /*!< Noise error         */
	//HAL_UART_ERROR_FE        = 0x04,    /*!< frame error         */
	//HAL_UART_ERROR_ORE       = 0x08,    /*!< Overrun error       */
	//HAL_UART_ERROR_DMA       = 0x10,    /*!< DMA transfer error  */
	//HAL_UART_ERROR_BUSY      = 0x20     /*!< Busy Error          */

	if( HAL_UART_ERROR_NONE != huart->ErrorCode)
	{
		//debug
		memset( G_u8_UartRxPayload, huart->ErrorCode, sizeof(G_u8_UartRxPayload) );
	}
}
/* USER CODE END 1 */
/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
