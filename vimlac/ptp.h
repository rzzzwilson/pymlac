/*
 * Interface for the imlac PTP (papertape punch).
 */

#ifndef PTP_H
#define PTP_H

int ptp_mount(char *fname);
void ptp_dismount(void);
void ptp_start(void);
void ptp_stop(void);
int ptp_punch(BYTE value);
bool ptp_ready(void);
void ptp_tick(long cycles);

#endif
