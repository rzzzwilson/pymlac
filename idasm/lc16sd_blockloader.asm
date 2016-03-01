;-----------------------
; 'lc16sd' blockloader code
; disassembled from munch.ptp
;-----------------------
	ORG	03700	; addr  code

ldaddr	RCF		; 03700 0001032
numwrd	JMS	.	; 03701 0037701 get address of 'chksum' into 'numwrd'

chksum	LAC	numwrd	; 03702 0063701 are we are running in high memory (017700+)
	SAM	himem	; 03703 0077775
	JMP	rdblk	; 03704 0013710 if not, just load tape

	LWC	012     ; 03705 0104012 else turn on the display
	DLA		; 03706 0001003
	DON		; 03707 0003100

rdblk	CAL		; 03710 0100011 initialize block checksum
	DAC	chksum	; 03711 0023702
	JMS	rdword	; 03712 0037746 get load address
	DAC	ldaddr	; 03713 0023700
	ASP		; 03714 0002002 if high bit set
	JMP	ldend	; 03715 0013740 then end of tape load
	JMS	rdword	; 03716 0037746 else get number of words in block
	DAC	numwrd	; 03717 0023701
	JMS	rdword	; 03720 0037746 read checksum word, add to checksum
blklp	JMS	rdword	; 03721 0037746 get data word
	DAC	*ldaddr	; 03722 0123700 store into memory
	LAC	ldaddr	; 03723 0063700 get load address
	SAR	3	; 03724 0003063 echo load address in display (if running)
	AND	low10	; 03725 0047765
	IOR	dlya0	; 03726 0053764
	DAC	disp	; 03727 0023766
	LAC	*ldaddr	; 03730 0163700 get last data word
	ISZ	ldaddr	; 03731 0033700 move 'load address' pointer
	ISZ	numwrd	; 03732 0033701 check end of block
	JMP	blklp	; 03733 0013721 jump if not ended
	ADD	chksum	; 03734 0067702 block end, check checksum
	ASZ		; 03735 0002001 if checksum invalid,
	JMP	.	; 03736 0013736     busy wait here
	JMP	rdblk	; 03737 0013710 else go get next block
; end of load, AC is load address, high bit set
ldend	DOF		; 03740 0001012 turn off the display
	IAC		; 03741 0100004
	ASN		; 03742 0102001 if address is 0177777
	HLT		; 03743 0000000     then just halt
	JMS	rdword	; 03744 0037746 else get AC contents
	JMP	*ldaddr	; 03745 0113700 and jump to start address
; read a word from tape, leave in AC
rdword	DATA	0	; 03746 0000000
	ADD	chksum	; 03747 0067702
	DAC	chksum	; 03750 0023702
	CAL		; 03751 0100011
	RSF		; 03752 0002040
	JMP	.-1	; 03753 0013752
	RRC		; 03754 0001033
	RAL	3	; 03755 0003003
	RAL	3	; 03756 0003003
	RAL	2	; 03757 0003002
	RSF		; 03760 0002040
	JMP	.-1	; 03761 0013760
	RRC		; 03762 0001033
	JMP	*rdword	; 03763 0113746

dlya0	DLYA	0	; 03764 0020000
low10	DATA	001777	; 03765 0001777

; display routine, used if running in extended memory
disp	DLYA	00000	; 03766 0020000
	DLXA	00000	; 03767 0010000
	DSTS	1	; 03770 0004005
	data	0046000	;DLVH	02000	; 03771 0046000
	DLYA	01777	; 03772 0021777
	DHLT		; 03773 0000000

	DATA	0067766	; 03774 0067766
himem	DATA	0017702	; 03775 0017702
	DATA	0010000	; 03776 0010000
	DATA	0177777	; 03777 0177777
	DATA	0000000	; 04000 0000000

	END		;
