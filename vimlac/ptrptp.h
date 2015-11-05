/*
 * Interface for the vimlac PTR/PTP (papertape reader/punch).
 */

#ifndef PTRPTP_H
#define PTRPTP_H

void ptrptp_reset(void);
int ptr_mount(char *fname);
void ptr_dismount(void);
void ptr_start(void);
void ptr_stop(void);
int ptr_read(void);
void ptr_tick(long cycles);
bool ptr_ready(void);

int ptp_mount(char *fname);
void ptp_dismount(void);
void ptp_start(void);
void ptp_stop(void);
void ptp_punch(BYTE byte);
void ptp_tick(long cycles);
bool ptp_ready(void);

#endif
