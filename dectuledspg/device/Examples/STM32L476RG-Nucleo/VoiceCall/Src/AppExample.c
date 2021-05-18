/* SPDX-License-Identifier: MIT */

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///
/// @file       AppExample.c
/// @brief      This is a Single threaded example with UART Rx interrupt without Operational system.
///             This example shows how to send a voice call start/end/answer request.
///
/// @details    Initialization:
///                 - Incoming UART data is passed to CmndLib from the UART interrupt (stm32l4xx_it.c)
///                 - The expansion board reset is released, it's HelloInd will be received
///             An Infinite loop waits for a button press:
///                 - HAL_GPIO_ReadPin() reads current button state
///                 - A green LED on Nucleo board is used to indicate the call start/end/answer request result:
///                   1 long blink:   call start/end/answer request was successful
///                   1 short blink:  call start request was not sent because the device is not registered
///                   2 short blinks: call start/end/answer request was not sent because of UART problems
///                   3 short blinks: call start/end/answer request was not successful because it was not accepted by
///                                   the DU-EB or the base (e.g. when the base is powered down)
///                   short blinks:   voice call from base indication, press blue button to answer the call
///             The following action is performed:
///                 - Blue button press:
///                   If device is registered: send voice call start/end/answer request (depending on call state)
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

// The voice call unit
#define DSPG_VOICE_CALL_UNIT_NUMBER  1

#define IE_SETTING_DEF_DIGITS       "123"
#define IE_SETTING_DEF_PARTY_NAME   "Party"
#define IE_SETTING_DEF_PARTY_ID     "PartyId"
#define IE_SETTING_DEF_PARTY_TYPE   "PartyType"

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

typedef enum
{
    CALL_IDLE,         // idle state
    CALL_PENDING,      // waiting for call answering
    CALL_ACTIVE,       // active state
}
t_en_CallState;

// Handle button state change
static t_en_ButtonMovement p_HandleButton( t_st_Button *pst_Button, bool CurrentState );

// Send voice call start message
static bool ExampleSendVoiceCallStartMessage( void );

// Send voice call end message
static bool ExampleSendVoiceCallEndMessage( void );

// Send voice call end call response message
static bool ExampleSendVoiceEndCallResMessage( void );

// Send voice call start call response message
static bool ExampleSendVoiceStartCallResMessage( void );

// handler for Hello indication from DU-EB
static void ExampleHandleHelloInd( t_st_Msg* pst_Msg );

// handler for Link Confirm from DU-EB
static void ExampleHandleLinkCfm( t_st_Msg* pst_Msg );

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

static int             g_GotLinkCfmResponse;
static int             g_GotHelloInd;

static t_en_CallState  g_VoiceCallState;
static int             g_GotVoiceCallStartInd;
static int             g_GotVoiceCallStartCfm;
static int             g_GotVoiceCallEndInd;
static int             g_GotVoiceCallEndCfm;
static int             g_GotVoiceCallRelInd;
static int             g_GotVoiceCallConnInd;

static int             g_EnableBlink = 0;
static int             g_BlinkOn = 0;


void ExampleMain( void )
{
    printf("\n");
    log_info("VoiceCall Example Started\n");
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

        if ( g_GotVoiceCallStartInd != 0 )
        {
            log_info( "Got Voice Call Start indication\n");
            g_GotVoiceCallStartInd = 0;
            g_VoiceCallState = CALL_PENDING;
            g_EnableBlink = 1;

            // option to automatically answer the call without pressing the blue button
            //log_info("Send Voice Call Start response with code CMND_RC_OK\n");
            //ExampleSendVoiceStartCallResMessage();
            //g_VoiceCallState = CALL_ACTIVE;
            //g_EnableBlink = 0;
        }

        if ( g_GotVoiceCallStartCfm != 0 )
        {
            log_info( "Got Voice Call Start confirmation\n");
            g_GotVoiceCallStartCfm = 0;
        }

        if ( g_GotVoiceCallEndInd != 0 )
        {
            log_info( "Got Voice Call End indication\n");
            g_GotVoiceCallEndInd = 0;

            log_info("Send Voice Call End response with code CMND_RC_OK\n");
            ExampleSendVoiceEndCallResMessage();
            g_VoiceCallState = CALL_IDLE;

            g_EnableBlink = 0;
            HAL_GPIO_WritePin( LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET );  // Turn off the LED
        }

        if ( g_GotVoiceCallEndCfm != 0 )
        {
            log_info( "Got Voice Call End confirmation\n");
            g_GotVoiceCallEndCfm = 0;
        }

        if ( g_GotVoiceCallRelInd != 0 )
        {
            log_info( "Got Voice Call Release indication\n");
            g_GotVoiceCallRelInd = 0;

            // return to idle state
            g_VoiceCallState = CALL_IDLE;
        }

        if ( g_GotVoiceCallConnInd != 0 )
        {
            log_info( "Got Voice Call Connected indication\n");
            g_GotVoiceCallConnInd = 0;

            ExampleSuccessIndication();

            // go to active state
            g_VoiceCallState = CALL_ACTIVE;
        }

        // Detect button state change
        en_ButtonMovement = p_HandleButton( &g_st_Button, !HAL_GPIO_ReadPin( B1_GPIO_Port, B1_Pin ) );

        if ( en_ButtonMovement == BUTTON_PRESSED)
        {
            // If device registered
            if ( g_Registered )
            {
                if ( g_VoiceCallState == CALL_IDLE )
                {
                    // Start voice call
                    log_info("Send start voice call request\n");
                    ExampleSendVoiceCallStartMessage();
                }
                else if ( g_VoiceCallState == CALL_ACTIVE )
                {
                    // End voice call
                    log_info("Send end voice call request\n");
                    ExampleSendVoiceCallEndMessage();
                }
                else if ( g_VoiceCallState == CALL_PENDING )
                {
                    // Answer voice call
                    log_info("Send Voice Call Start response with code CMND_RC_OK\n");
                    ExampleSendVoiceStartCallResMessage();
                    g_VoiceCallState = CALL_ACTIVE;
                    g_EnableBlink = 0;
                    HAL_GPIO_WritePin( LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET );  // Turn off the LED
                }
            }
            else
            {
                log_warn( "Device not registered\n" );
                ExampleFailureIndication(1);
            }
        }

        if ( g_EnableBlink )
        {
            if ( g_BlinkOn )
            {
                HAL_GPIO_WritePin( LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET );  // Turn off the LED
                HAL_Delay( 100 ); // Short delay
                g_BlinkOn = 0;
            }
            else
            {
                HAL_GPIO_WritePin( LD2_GPIO_Port, LD2_Pin, GPIO_PIN_SET );    // Turn on the LED
                HAL_Delay( 100 );
                g_BlinkOn = 1;
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

        case CMND_SERVICE_ID_ULE_VOICE_CALL:
        {
            if (g_st_Msg.messageId == CMND_MSG_ULE_CALL_START_IND)
            {
                g_GotVoiceCallStartInd = 1;
            }
            else if (g_st_Msg.messageId == CMND_MSG_ULE_CALL_START_CFM)
            {
                g_GotVoiceCallStartCfm = 1;
            }
            else if (g_st_Msg.messageId == CMND_MSG_ULE_VOICE_CALL_END_IND)
            {
                g_GotVoiceCallEndInd = 1;
            }
            else if (g_st_Msg.messageId == CMND_MSG_ULE_VOICE_CALL_END_CFM)
            {
                g_GotVoiceCallEndCfm = 1;
            }
            else if (g_st_Msg.messageId == CMND_MSG_ULE_VOICE_CALL_CONNECTED_IND)
            {
                g_GotVoiceCallConnInd = 1;
            }
            else if (g_st_Msg.messageId == CMND_MSG_ULE_VOICE_CALL_RELEASE_IND)
            {
                g_GotVoiceCallRelInd = 1;
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

// Send Voice Call start message to remote
bool ExampleSendVoiceCallStartMessage( void )
{
    t_st(CMND_IE_ULE_CALL_SETTING) st_CallSettings;
    t_st_Packet st_Packet = { 0 };

    st_CallSettings.u32_FieldMask = ULE_CALL_IE_PREFFERED_CODEC_MASK |
                                    ULE_CALL_IE_OTHER_PARTY_NAME_MASK |
                                    ULE_CALL_IE_DIGITS_MASK;

    st_CallSettings.u8_DigitsLen = sizeof( IE_SETTING_DEF_DIGITS );
    memcpy( st_CallSettings.pu8_Digits, IE_SETTING_DEF_DIGITS,
            st_CallSettings.u8_DigitsLen );

    st_CallSettings.u8_OtherPartyNameLen = sizeof( IE_SETTING_DEF_PARTY_NAME );
    memcpy( st_CallSettings.pu8_OtherPartyName, IE_SETTING_DEF_PARTY_NAME,
            st_CallSettings.u8_OtherPartyNameLen );

    st_CallSettings.u8_OtherPartyIdLen = sizeof( IE_SETTING_DEF_PARTY_ID );
    memcpy( st_CallSettings.pu8_OtherPartyId, IE_SETTING_DEF_PARTY_ID,
            st_CallSettings.u8_OtherPartyIdLen );

    st_CallSettings.u8_PreferredCodec = 1;

    p_VoiceCall_StartCallReq(&st_Packet, DSPG_VOICE_CALL_UNIT_NUMBER, &st_CallSettings);

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

// Send Voice Call end message to remote
bool ExampleSendVoiceCallEndMessage( void )
{
    t_st_Packet st_Packet = { 0 };

    p_VoiceCall_EndCallReq(&st_Packet, DSPG_VOICE_CALL_UNIT_NUMBER);

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

// Send Voice Call start call response message to remote
bool ExampleSendVoiceStartCallResMessage( void )
{
    t_st(CMND_IE_ULE_CALL_SETTING) st_CallSettings;
    t_st_Packet st_Packet = { 0 };

    st_CallSettings.u32_FieldMask = ULE_CALL_IE_PREFFERED_CODEC_MASK |
                                    ULE_CALL_IE_OTHER_PARTY_NAME_MASK |
                                    ULE_CALL_IE_DIGITS_MASK;

    st_CallSettings.u8_DigitsLen = sizeof( IE_SETTING_DEF_DIGITS );
    memcpy( st_CallSettings.pu8_Digits, IE_SETTING_DEF_DIGITS,
            st_CallSettings.u8_DigitsLen );

    st_CallSettings.u8_OtherPartyNameLen = sizeof( IE_SETTING_DEF_PARTY_NAME );
    memcpy( st_CallSettings.pu8_OtherPartyName, IE_SETTING_DEF_PARTY_NAME,
            st_CallSettings.u8_OtherPartyNameLen );

    st_CallSettings.u8_OtherPartyIdLen = sizeof( IE_SETTING_DEF_PARTY_ID );
    memcpy( st_CallSettings.pu8_OtherPartyId, IE_SETTING_DEF_PARTY_ID,
            st_CallSettings.u8_OtherPartyIdLen );

    st_CallSettings.u8_PreferredCodec = 1;

    p_VoiceCall_StartCallRes(&st_Packet, DSPG_VOICE_CALL_UNIT_NUMBER, CMND_RC_OK, &st_CallSettings);
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

// Send Voice Call end call response message to remote
bool ExampleSendVoiceEndCallResMessage( void )
{
    t_st_Packet st_Packet = { 0 };

    p_VoiceCall_EndCallRes(&st_Packet, DSPG_VOICE_CALL_UNIT_NUMBER, CMND_RC_OK);

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
