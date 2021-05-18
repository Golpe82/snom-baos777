/* SPDX-License-Identifier: MIT */
#ifndef __LOG_H_
#define __LOG_H_

#ifdef __cplusplus
 extern "C" {
#endif

void log_info(char *fmt, ...);
void log_warn(char *fmt, ...);

#ifdef __cplusplus
 }
#endif

#endif /* __LOG_H_ */
