	ORG	100'	; Program to display hello in center of screen
	DOF		; Stop display
R:	DSN		; Skip if display off  Restart point
	JMP	.-1
	SSF		; Skip if 40 cycle sync on
	JMP	.-1
	SCF		; Clear 40 cycle sync
	LDA		; DS go to AC
	AND	[100000']
	DAC	.+1
	BSS	1	; Halt or continue depending on DS0
	LAW	D	; LAW start address of display routine
	DLA		; C(AC) go to C(DPC)
	DON		; Start display
	JMP	R	; Wait for next cycle of display accumulator
D:	DLXA	4000'	; Load 4000 into X display accumulator
	DLYA	4000'	; Load 4000 into Y AC
	DSTS	1	; Set scale 1
	DHVC		; High voltage sync and continue
	DJMS	H	; Display JMS to H character description
	DJMS	E	; Display JMS to E character description
	DJMS	L	; Display JMS to L character description
	DJMS	L	; Display JMS to L character description
	DJMS	O	; Display JMS to O character description
	DLXA	4000'	; Center beam to minimize load on deflection amplifier
	DLYA	4000'
	DHLT		; Stop display
H:	INC	E,B03	; H character description
	INC	B03,B02
	INC	D30,D30
	INC	B0M3,B0M3
	INC	B0M2,D03
	INC	D01,BM30
	INC	BM30,F
E:	INC	E,B03	; E character description
	INC	B03,B02
	INC	B30,B30
	INC	DM1M3,DM1M1
	INC	BM30,BM10
	INC	D0M3,D0M1
	INC	B30,B30
	INC	F,F	; (needed 2 bytes to fill out word)
L:	INC	E,B03	; L character description
	INC	B03,B02
	INC	1,P
	INC	B30,B30
	INC	F,F
O:	INC	E,D02	; O character description
	INC	B03,B23
	INC	B20,B2M3
	INC	B0M3,BM2M2
	INC	BM20,BM22
	INC	F,F
	END	100'
