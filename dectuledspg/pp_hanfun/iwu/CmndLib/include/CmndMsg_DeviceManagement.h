/*
 * Copyright (c) 2016-2018 DSP Group, Inc.
 *
 * SPDX-License-Identifier: MIT
 */
#ifndef _CMND_MSG_DEVICE_MANAGEMENT_H
#define _CMND_MSG_DEVICE_MANAGEMENT_H

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

#include "TypeDefs.h"
#include "CmndApiExported.h"

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

extern_c_begin

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
/// @brief  Create DeviceManagement register packet buffer based on given parameters.
///         The <pst_hanCmndApiMsg> will contain all CMND API message fields.
///         Data is stored in network order.
///
/// @param[out]     pst_hanCmndApiMsg       - pointer to message
/// @param[in]      pst_baseWanted          - NULL or pointer to t_st_hanCmndIeBaseWanted if specified base address wanted
///
/// @return     true when success
//////////////////////////////////////////////////////////////////////////////
bool p_Cmnd_DeviceManagement_CreateRegisterDeviceReq(   OUT t_st_hanCmndApiMsg*         pst_hanCmndApiMsg,
                                                        const t_st_hanCmndIeBaseWanted* pst_baseWanted );


//////////////////////////////////////////////////////////////////////////////
/// @brief  Create DeviceManagement deregister packet buffer based on given parameters.
///         The <pst_hanCmndApiMsg> will contain all CMND API message fields.
///         Data is stored in network order.
///
/// @param[out]     pst_hanCmndApiMsg   - pointer to message
///
/// @return     true when success
//////////////////////////////////////////////////////////////////////////////
bool p_Cmnd_DeviceManagement_CreateDeregisterDeviceReq( OUT t_st_hanCmndApiMsg* pst_hanCmndApiMsg );

extern_c_end

#endif // _CMND_MSG_DEVICE_MANAGEMENT_H
