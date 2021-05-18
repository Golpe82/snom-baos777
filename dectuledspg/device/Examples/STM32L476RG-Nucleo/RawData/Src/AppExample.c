/* SPDX-License-Identifier: MIT */

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///
/// @file       AppExample.c
/// @brief      This is a Single threaded example with UART Rx interrupt without Operational system.
///             This example shows how to send a Raw FUN message.
///
/// @details    Initialization:
///                 - Incoming UART data is passed to CmndLib from the UART interrupt (stm32l4xx_it.c)
///                 - The expansion board reset is released, it's HelloInd will be received
///             An Infinite loop waits for a button press:
///                 - HAL_GPIO_ReadPin() reads current button state
///                 - A green LED on Nucleo board is used to indicate the alert request result:
///                   1 long blink:   send raw FUN message request was successful
///                   1 short blink:  send raw FUN message request was not sent because the device is not registered
///                   2 short blinks: send raw FUN message request was not sent because of UART problems
///                   3 short blinks: send raw FUN message request was not successful because it was not accepted by the
///                                   DU-EB or the base (e.g. when the base is powered down)
///             The following action is performed:
///                 - Blue button press:
///                   If device is registered: send Raw FUN message
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

// The raw data unit and interface
#define DSPG_RAW_DATA_UNIT_NUMBER       (3)
#define DSPG_RAW_DATA_INTERFACE_ID      (0x7f16)

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

// Send raw FUN message with up to 128 bytes to remote
static bool ExampleSendRawFunMessage( u16 g_DeviceId, u8* pu8_Data, u16 u16_DataSize );

// handler for Hello indication from DU-EB
static void ExampleHandleHelloInd( t_st_Msg* pst_Msg );

// handler for Link Confirm from DU-EB
static void ExampleHandleLinkCfm( t_st_Msg* pst_Msg );

// handler for FUN Message receive indication
void ExampleHandleFunRecvInd( t_st_Msg* pst_Msg );

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
static u8              g_RawDataLen;
static u8              g_RawData[40];

static int             g_GotLinkCfmResponse;
static int             g_GotRawFunReceiveInd;
static int             g_GotHelloInd;


void ExampleMain( void )
{
    printf("\n");
    log_info("RawData Example Started\n");
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

            if ( g_SendResult == 0 )
            {
                ExampleSuccessIndication();
            }
            else
            {
                ExampleFailureIndication(3);
            }
        }

        if (  g_GotRawFunReceiveInd != 0 )
        {
            char buf[g_RawDataLen+1];

            memcpy(buf, g_RawData, g_RawDataLen);
            buf[g_RawDataLen] = '\0';

            log_info( "Got Raw FUN message: '%s'\n", buf );

            g_GotRawFunReceiveInd = 0;
            ExampleSuccessIndication();
        }


        // Detect button state change
        en_ButtonMovement = p_HandleButton( &g_st_Button, !HAL_GPIO_ReadPin( B1_GPIO_Port, B1_Pin ) );

        if ( en_ButtonMovement == BUTTON_PRESSED)
        {
            // If device registered
            if ( g_Registered )
            {
                // Send Raw FUN message
                u8 u8_RawData[] = "Hello, World!";
                log_info( "Send raw FUN request\n");
                ExampleSendRawFunMessage( g_DeviceId, u8_RawData, sizeof(u8_RawData)-1	 );
            }
            else
            {
                log_warn( "Device not registered\n" );
                ExampleFailureIndication(1);
            }
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

        case CMND_SERVICE_ID_FUN:
        {
            if ( g_st_Msg.messageId == CMND_MSG_FUN_RECV_IND )
            {
                ExampleHandleFunRecvInd(&g_st_Msg);
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

// Send raw FUN message with up to 128 bytes to remote
bool ExampleSendRawFunMessage( u16 u16_DeviceId, u8* pu8_Data, u16 u16_DataSize )
{
    t_st_hanCmndIeFun st_IeFun = { 0 };
    t_st_Packet st_Packet = { 0 };

    if (u16_DataSize > CMND_IE_FUN_MAX_DATA_SIZE)
        return false;

    // prepare FUN IE structure
    st_IeFun.u16_SrcDeviceId = u16_DeviceId; // from our ID
    st_IeFun.u8_SrcUnitId = DSPG_RAW_DATA_UNIT_NUMBER;
    st_IeFun.u16_DstDeviceId = 0; // to Base
    st_IeFun.u8_DstUnitId = 2;

    st_IeFun.u16_InterfaceId = DSPG_RAW_DATA_INTERFACE_ID;
    st_IeFun.u8_InterfaceType = 1;
    st_IeFun.u8_InterfaceMember = 1;
    st_IeFun.u8_AddressType = 0;
    st_IeFun.u16_DataLen = u16_DataSize;
    st_IeFun.u8_MessageType = CMND_FUN_MSG_TYPE_COMMAND;

    // copy the data into FUN structure (with limit of memory available to hold the buffer)
    memcpy( st_IeFun.pu8_Data, pu8_Data, st_IeFun.u16_DataLen );

    // send to base
    p_Fun_SendReq( &st_Packet, &st_IeFun );

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
        {
            g_SendResult = st_IeResponse.u8_Result;
        }
    }
    g_GotLinkCfmResponse = 1;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

void ExampleHandleFunRecvInd( t_st_Msg* pst_Msg )
{
    t_st(CMND_IE_FUN) st_IeFun;

    // extract result, store into global g_SendResult
    if ( !p_CmndMsg_IeGet(IN pst_Msg, p_CMND_IE_GETTER(CMND_IE_FUN), &st_IeFun, sizeof(st_IeFun) ) )
    {
        // Error while extracting information element
        return;
    }

    // is this for unit 3, our raw data unit?
    if (st_IeFun.u8_DstUnitId == 3)
    {
        g_RawDataLen = st_IeFun.u16_DataLen;
        memcpy(g_RawData, st_IeFun.pu8_Data, g_RawDataLen);
        g_GotRawFunReceiveInd = 1;
    }
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
