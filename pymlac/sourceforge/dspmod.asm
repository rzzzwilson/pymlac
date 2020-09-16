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
	LTORG
D:	DLXA	1000'	; Center beam
	DLYA	1000'
	DHVS	1	; High voltage sync and set scale 1
	DJMS	H	; Display JMS to H character description
	DJMS	E	; Display JMS to E character description
	DJMS	L	; Display JMS to L character description
	DJMS	L	; Display JMS to L character description
	DJMS	O	; Display JMS to O character description
	DLXA	1000'	; Center beam to minimize load on deflection amplifier
	DLYA	1000'
	DSTB	1		; Set for reference to upper 4K
	DJMS	400'		; Draw horizontal vector and return to center
	DSTB	0		; Reset to lower 4K
	DATA	4001'		; DADR - turn on MIT mod
	DATA	150300'		; Try MIT DJMS reference to upper 4K
	DLXA	1000'	; Center beam to minimize load on deflection amplifier
	DLYA	1000'
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
	;; Catch failed MIT DJMS to 10300
	;; Draw a diagonal line toward the bottom right of the screen
	;; and return to center
	ORG	300'
	DLV	B,777',-1000'
	DLV	D,-777',1000'
	DRJM
	;; Catch failed DSTB 1 DJMS to 10400
	;; Draw a diagonal line toward the bottom left of the screen
	;; and return to center
	ORG	400'
	DLV	B,-1000',-1000'
	DLV	D,1000',1000'
	DRJM
	;; Catch a successful MIT DJMS to 10300
	;; Draw a vertical line to the top of the screen and
	;; return to center
	ORG	10300'
	DLV	B,0,777'
	DLV	D,0,-777'
	DRJM
	;; Catch successful DSTB 1 DJMS to 10400
	;; Draw a horizontal line to the left side of the screen
	;; and return to center
	ORG	10400'
	DLV	B,-1000',0
	DLV	D,1000',0
	DRJM
	END	100'
