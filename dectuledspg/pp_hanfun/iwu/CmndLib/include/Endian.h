/*
 * Copyright (c) 2016-2018 DSP Group, Inc.
 *
 * SPDX-License-Identifier: MIT
 */
#ifndef _ENDIAN_H
#define _ENDIAN_H

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

#include "TypeDefs.h"

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////
/// Enum of endian types
///////////////////////////////////////////////////////////////////////////////
typedef enum
{
    ENDIAN_LITTLE = 0,
    ENDIAN_BIG = 1,
    ENDIAN_PDP = 2,
    ENDIAN_UNKNOWN = (int)0xFFFFFFFF
} t_en_Endianness;

///////////////////////////////////////////////////////////////////////////////
/// A macro that can be used to help determine a program's endianness
/// at compile-time.
///////////////////////////////////////////////////////////////////////////////
#define ENDIANNESS_PROBE (1u & 0xFFFFFFFFu)
#define ENDIANNESS \
    (\
     (ENDIANNESS_PROBE == 0x00000001u) ?\
     ENDIAN_LITTLE :\
     (\
      (ENDIANNESS_PROBE == 0x01000000u) ?\
      ENDIAN_BIG :\
      (\
       (ENDIANNESS_PROBE == 0x00010000u) ?\
       ENDIAN_PDP :\
       ENDIAN_UNKNOWN\
      )\
     )\
    )

///////////////////////////////////////////////////////////////////////////////
/// A macro to check is little endian
///////////////////////////////////////////////////////////////////////////////
#define ENDIANNESS_IS_LITTLE ( ENDIANNESS == ENDIAN_LITTLE )

///////////////////////////////////////////////////////////////////////////////
/// A macro to check is big endian
///////////////////////////////////////////////////////////////////////////////
#define ENDIANNESS_IS_BIG ( ENDIANNESS == ENDIAN_BIG )

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

extern_c_begin

///////////////////////////////////////////////////////////////////////////////
/// Convert u16 from Host bytes endian to Network endian
///////////////////////////////////////////////////////////////////////////////
u16 p_Endian_hos2net16( u16 u16_Value );

///////////////////////////////////////////////////////////////////////////////
/// Convert u32 from Host bytes endian to Network endian
///////////////////////////////////////////////////////////////////////////////
u32 p_Endian_hos2net32( u32 u32_Value );

///////////////////////////////////////////////////////////////////////////////
/// Convert u16 from Network bytes endian to Host bytes endian
///////////////////////////////////////////////////////////////////////////////
u16 p_Endian_net2hos16( u16 u16_Value );

///////////////////////////////////////////////////////////////////////////////
/// Convert u32 from Network bytes endian to Host bytes endian
///////////////////////////////////////////////////////////////////////////////
u32 p_Endian_net2hos32( u32 u32_Value );

///////////////////////////////////////////////////////////////////////////////
/// Reorder bytes endian for u16
///////////////////////////////////////////////////////////////////////////////
u16 p_Endian_Reorder16( u16 u16_Value );

///////////////////////////////////////////////////////////////////////////////
/// Reorder bytes endian for u32
///////////////////////////////////////////////////////////////////////////////
u32 p_Endian_Reorder32( u32 u32_Value );

extern_c_end

#endif // _ENDIAN_H
