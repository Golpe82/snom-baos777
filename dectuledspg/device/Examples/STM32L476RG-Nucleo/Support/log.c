/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <stdarg.h>
#include "log.h"
#include "main_extern.h"

void log_info(char *fmt, ...)
{
    va_list ap;

    printf("[*] %08lu ", HAL_GetTick());

    va_start(ap, fmt);
    vprintf(fmt, ap);
    va_end(ap);
}

void log_warn(char *fmt, ...)
{
    va_list ap;

    printf("[!] %08lu ", HAL_GetTick());

    va_start(ap, fmt);
    vprintf(fmt, ap);
    va_end(ap);
}
