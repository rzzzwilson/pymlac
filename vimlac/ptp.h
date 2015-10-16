/*
 * Interface for the vimlac PTP (papertape punch).
 */

#ifndef PTP_H
#define PTP_H

int ptp_mount(char *fname);
void ptp_dismount(void);
void ptp_start(void);
void ptp_stop(void);
void ptp_punch(BYTE byte);
void ptp_tick(long cycles);
bool ptp_ready(void);

#endif
