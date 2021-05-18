/* SPDX-License-Identifier: MIT */

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///
/// @file       AppExample.c
/// @brief      This is a Single threaded example with UART Rx interrupt without Operational system.
///             This example shows how to send a registration request.
///
/// @details    Initialization:
///                 - Incoming UART data is passed to CmndLib from the UART interrupt (stm32l4xx_it.c)
///                 - The expansion board reset is released, it's HelloInd will be received
///             An Infinite loop waits for a button press:
///                 - HAL_GPIO_ReadPin() reads current button state
///                 - A LED available on Nucleo board is used to indicate ...
///             The following action is performed:
///                 - Blue button press:
///                   send registration request message
///
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <stdio.h>
#include <string.h>
#include "CmndLib.h"
#include "main_extern.h"
#include "log.h"

// Minimum time to detect button pressed
#define BUTTON_ACTIVE_TIME              (10)

#define EXAMPLE_UART_SEND_TIMEOUT_MS    (100)

typedef enum
{
    BUTTON_INITIAL,         // initial state
    BUTTON_PENDING,         // pending
}
t_en_ButtonState;

typedef enum
{
    BUTTON_NOCHANGE,
    BUTTON_PRESSED,
}
t_en_ButtonMovement;

typedef struct
{
    u64  u64_StartTicks;
    bool b_Pressed;
    t_en_ButtonState en_State;
}
t_st_Button;

// Handle button state change
static t_en_ButtonMovement p_HandleButton( t_st_Button *pst_Button, bool CurrentState );

// Send registration request message
static bool ExampleSendRegistrationRequestMessage( void );

// handler for Hello indication from DU-EB
static void ExampleHandleHelloInd( t_st_Msg* pst_Msg );

// handler for Link Confirm from DU-EB
static void ExampleHandleLinkCfm( t_st_Msg* pst_Msg );

// handler for Register Confirmation from DU-EB
static void ExampleHandleRegisterCfm( t_st_Msg* pst_Msg );

// handler for Register Indication from DU-EB
static void ExampleHandleRegisterInd( t_st_Msg* pst_Msg );

// initialize context to zeros
static void ExampleInitParserContext(void);

// example function for writing a buffer to uart port + logging the buffer
static HAL_StatusTypeDef ExampleUartWrite( void* buffer, size_t bufferSize );

// LED control to indicate success or failure
static void ExampleSuccessIndication(void);
static void ExampleFailureIndication(u8 u8_Count);

// global state
static int g_Registered;
static int g_DeviceId;

// holds incoming CMND Message
static t_st_Msg        g_st_Msg;
static t_stReceiveData g_ParserContext;
t_st_Button            g_st_Button;

static u8              g_SendResult;

static int             g_GotHelloInd;
static u8              g_GotLinkCfmResponse;
static u8              g_GotRegisterInd;
static u8              g_GotRegisterCfm;

void ExampleMain( void )
{
    printf("\n");
    log_info("Register Example Started\n");
    printf("\n");

    // Initialize Parser Context
    ExampleInitParserContext();

    // Start booting the DU-EB by asserting GPIOA8 (connected to RST_N)
    HAL_Delay(100);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_8, GPIO_PIN_SET);

    // Infinite loop that waits for button press and executes an action
    while( 1 )
    {
        t_en_ButtonMovement en_ButtonMovement = BUTTON_NOCHANGE;

        // this is the first message received, once the DU-EB finished booting
        // following a power-on-reset or a software reset
        if ( g_GotHelloInd != 0 )
        {
            log_info( "Got Hello World indication\n");
            g_GotHelloInd = 0;

            if (!g_Registered)
            {
                log_warn("Device not registered, please register\n");
                ExampleFailureIndication(1);
            }
        }

        if ( g_GotLinkCfmResponse != 0 )
        {
            log_info( "Got LinkCfm response, result = 0x%x\n", g_SendResult );
            g_GotLinkCfmResponse = 0;
        }

		if ( g_GotRegisterCfm != 0 )
        {
            log_info( "Got Register Confirmation, result = 0x%x\n", g_SendResult );

            g_GotRegisterCfm = 0;

		    if ( g_SendResult == 0 )
            {
                // start registration succeeded
				// does not indicate that registration is completed successfully!
				ExampleSuccessIndication();
            }
            else
            {
                ExampleFailureIndication(3);
            }
        }

		if ( g_GotRegisterInd != 0 )
        {
            log_info( "Got Register Indication, result = 0x%x\n", g_SendResult );
            g_GotRegisterInd = 0;

		    if ( g_SendResult == 0 )
            {
 				// indicates that registration is completed successfully
		        log_info("Device is now registered!\n");
				ExampleSuccessIndication();
            }
            else
            {
                ExampleFailureIndication(3);
            }
        }

        // Detect button state change
        en_ButtonMovement = p_HandleButton( &g_st_Button, !HAL_GPIO_ReadPin( B1_GPIO_Port, B1_Pin ) );

        if ( en_ButtonMovement == BUTTON_PRESSED)
        {
            // Send registration request
            log_info("Send registration request\n");
            ExampleSendRegistrationRequestMessage();
        }
    }
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

void ExampleInitParserContext(void)
{
	memset(&g_ParserContext, 0, sizeof(t_stReceiveData));
}

// Example Code - Message Received from UART in CMND Format
// IMPORTANT - This is a IRQ context and therefore MUST avoid blocking UART Callback
// handling of received message must be quick and non blocking
// otherwise arriving data from uart will be lost
void ExampleCmndMessageReceived(void)
{
    p_CmndMsgLog_PrintRxMsg( &g_st_Msg );

    switch (g_st_Msg.serviceId)
	{
		case CMND_SERVICE_ID_GENERAL:
		{
            if (g_st_Msg.messageId == CMND_MSG_GENERAL_HELLO_IND)
            {
                // handle the hello indication, the first message sent by the
                // DU-EB after reset release and firmware boot
                ExampleHandleHelloInd(&g_st_Msg);
            }
            else if ( g_st_Msg.messageId == CMND_MSG_GENERAL_LINK_CFM )
            {
                // handle response to "Send Raw FUN" request
                // extract the transmission result
                ExampleHandleLinkCfm( &g_st_Msg );
            }
        }
		break;

	    case CMND_SERVICE_ID_DEVICE_MANAGEMENT:
		{
			if ( g_st_Msg.messageId == CMND_MSG_DEV_MGNT_REGISTER_DEVICE_CFM )
			{
                // handle confirmation to Registration request
                // extract the confirmation result
		        ExampleHandleRegisterCfm ( &g_st_Msg );
			}
			else if ( g_st_Msg.messageId == CMND_MSG_DEV_MGNT_REGISTER_DEVICE_IND )
			{
                // handle answer to "Registration" request
                // extract the registration result
		        ExampleHandleRegisterInd ( &g_st_Msg );
			}
		}
		break;
	}
}


///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

// UART Callback
// Minimal handling as it must return ASAP, called from IRQ context
void HAL_UART_RxCpltCallback( UART_HandleTypeDef *huart )
{
    if ( huart == G_hUart) {
        bool haveMessage = p_hanCmndApi_HandleByte(&g_ParserContext, G_u8_UartRxPayload[0], &g_st_Msg);
        if ( haveMessage)
        {
			ExampleCmndMessageReceived();
        }
        // Request UART read again to activate this IRQ
        HAL_UART_Receive_IT( huart,  G_u8_UartRxPayload, sizeof(G_u8_UartRxPayload) );
    }
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

// Send registration request message to remote
bool ExampleSendRegistrationRequestMessage( void )
{
    // Registration to base
    t_st_Packet        st_Packet = { 0 };

    // Build CMND register device request packet:
    // - register to any base
    // - to register to a specific base, supply a 5 byte array with the
    //   wannted RFPI instead of NULL
    p_DeviceManagement_RegisterDeviceReq( &st_Packet, NULL );

    if ( ExampleUartWrite( st_Packet.buffer, st_Packet.length )  != HAL_OK )
    {
        ExampleFailureIndication(2);
        return false;
    }
    return true;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////


// A helper function to detect that button is pressed
t_en_ButtonMovement p_HandleButton( t_st_Button *pst_Button, bool CurrentState )
{
    t_en_ButtonMovement en_ButtonMovement = BUTTON_NOCHANGE;
    u64 u64_CurrentTicks = (u64)HAL_GetTick(); //p_CmndLib_UserImpl_GetTickCountMs();

    // If state has changed
    if( CurrentState != pst_Button->b_Pressed )
    {
        if( !pst_Button->b_Pressed && CurrentState )
        {
            // Save event timestamp
            pst_Button->u64_StartTicks = u64_CurrentTicks;
            pst_Button->en_State = BUTTON_PENDING;
        }
        else if ( pst_Button->b_Pressed && !CurrentState )
        {
            if ( pst_Button->en_State == BUTTON_PENDING )
            {
                if ( ( u64_CurrentTicks - pst_Button->u64_StartTicks ) > BUTTON_ACTIVE_TIME )
                {
                    en_ButtonMovement = BUTTON_PRESSED;
                    pst_Button->en_State = BUTTON_INITIAL;
                }
            }
        }
        pst_Button->b_Pressed = CurrentState; // Save new state
    }
    return en_ButtonMovement;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

void ExampleHandleHelloInd( t_st_Msg* pst_Msg )
{
    t_st(CMND_IE_GENERAL_STATUS) st_IeGenStatus;

    // extract device id if registered, store into global g_DeviceId
    if ( p_CmndMsg_IeGet(IN pst_Msg, p_CMND_IE_GETTER(CMND_IE_GENERAL_STATUS), &st_IeGenStatus, sizeof(st_IeGenStatus) ) )
    {
        g_Registered = (CMND_GEN_STATUS_REGISTERED == st_IeGenStatus.u8_RegStatus);
        if (g_Registered)
        {
            g_DeviceId = st_IeGenStatus.u16_DeviceID;
        }
    }
    g_GotHelloInd = 1;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

void ExampleHandleLinkCfm( t_st_Msg* pst_Msg )
{
    t_st(CMND_IE_RESPONSE) st_IeResponse;

    // extract result, store into global g_SendResult
    if ( p_CmndMsg_IeGet(IN pst_Msg, p_CMND_IE_GETTER(CMND_IE_RESPONSE), &st_IeResponse, sizeof(st_IeResponse) ) )
    {
        g_SendResult = st_IeResponse.u8_Result;
    }
    g_GotLinkCfmResponse = 1;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

void ExampleHandleRegisterCfm( t_st_Msg* pst_Msg )
{
     t_st(CMND_IE_RESPONSE) st_IeResponse;

     // extract result, store into global g_u8_SendResult
	 if ( p_CmndMsg_IeGet(IN pst_Msg, p_CMND_IE_GETTER(CMND_IE_RESPONSE), &st_IeResponse, sizeof(st_IeResponse) ) )
     {
        g_SendResult = st_IeResponse.u8_Result;
	 }
	 g_GotRegisterCfm = 1;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

void ExampleHandleRegisterInd( t_st_Msg* pst_Msg )
{
    t_st_hanCmndIeRegistrationResponse  ieResponse = {0};

    // extract result, store into global g_SendResult
    // if successful, store device Id into global g_DeviceId
    if( p_CmndMsg_IeGet(IN pst_Msg, p_CMND_IE_GETTER(CMND_IE_REGISTRATION_RESPONSE), &ieResponse, sizeof(ieResponse) ) )
    {
        g_SendResult = ieResponse.u8_ResponseCode;
        g_DeviceId = ieResponse.u16_DeviceAddress;

        if (g_SendResult == 0)
        {
           // Registration successful
           g_Registered = 1;
        }
        else
        {
           g_Registered = 0;
        }
    }
    g_GotRegisterInd = 1;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

HAL_StatusTypeDef ExampleUartWrite( void* buffer, size_t bufferSize )
{
    p_CmndMsgLog_PrintTxBuffer(bufferSize, buffer);
    return HAL_UART_Transmit( G_hUart, buffer, bufferSize, EXAMPLE_UART_SEND_TIMEOUT_MS );
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

void ExampleSuccessIndication( void )
{
    HAL_GPIO_WritePin( LD2_GPIO_Port, LD2_Pin, GPIO_PIN_SET );    // Turn on the LED
    HAL_Delay( 500 );                                             // Short delay
    HAL_GPIO_WritePin( LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET );  // Turn off the LED
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

void ExampleFailureIndication( u8 u8_Count )
{
    u8 u8_i;

    for (u8_i = 0; u8_i < u8_Count; u8_i++ )
    {
        HAL_GPIO_WritePin( LD2_GPIO_Port, LD2_Pin, GPIO_PIN_SET );    // Turn on the LED
        HAL_Delay( 100 );                                             // Short delay
        HAL_GPIO_WritePin( LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET );  // Turn off the LED
        HAL_Delay( 100 );                                             // Short delay
    }
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
