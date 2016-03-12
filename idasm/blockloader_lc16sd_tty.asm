; a lc16sd blockloader for TTYIN, with visual display.
; disassembled from iasm/simpledisplay2.ptp.
	ORG	03700	; addr  code

addr	RCF		; 03700 0001032
blkcnt	JMS	.	; 03701 0037701
cksum	LAC	blkcnt	; 03702 0063701
	SAM	hiaddr	; 03703 0077775
	JMP	rdblk	; 03704 0013710
	LWC	00012	; 03705 0104012
	DLA		; 03706 0001003
	DON		; 03707 0003100
rdblk	CAL		; 03710 0100011
	DAC	cksum	; 03711 0023702 ; clear checksum
	JMS	rdword	; 03712 0037746 ; get block load address
	DAC	addr	; 03713 0023700
	ASP		; 03714 0002002 ; skip if positive
	JMP	endtty	; 03715 0013740 ; else end-of-data
	JMS	rdword	; 03716 0037746 ; get 16bit data word count
	DAC	blkcnt	; 03717 0023701
	JMS	rdword	; 03720 0037746 ; get checksum from TTY
nxtwrd	JMS	rdword	; 03721 0037746 ; get data word
	DAC	*addr	; 03722 0123700 ; store in memory
	LAC	addr	; 03723 0063700 ; update display
	SAR	3	; 03724 0003063
	AND	L03765	; 03725 0047765
	IOR	L03764	; 03726 0053764
	DAC	L03766	; 03727 0023766
	LAC	*addr	; 03730 0163700
	ISZ	addr	; 03731 0033700 ; bump address for next word
	ISZ	blkcnt	; 03732 0033701 ; block finished?
	JMP	nxtwrd	; 03733 0013721 ; if not, get next data word
	ADD	cksum	; 03734 0067702
	ASZ		; 03735 0002001 ; skip if checksum OK
	JMP	.	; 03736 0013736 ; if not, busy wait here
	JMP	rdblk	; 03737 0013710
;--------------------------------------
; end of data, display off, autostart if specified
;--------------------------------------
endtty	DOF		; 03740 0001012 ; display off
	IAC		; 03741 0100004 ; 
	ASN		; 03742 0102001 ; 
	HLT		; 03743 0000000 ; stop here if no autostart
	JMS	rdword	; 03744 0037746 ; get AC contents
	JMP	*addr	; 03745 0113700 ; goto loaded code
;--------------------------------------
; read a word from TTYIN, updating checksum with word in AC
;--------------------------------------
rdword	DATA	0	; 03746 0000000
	ADD	cksum	; 03747 0067702
	DAC	cksum	; 03750 0023702 ; update checksum
	CAL		; 03751 0100011
	RSF		; 03752 0002040
	JMP	.-1	; 03753 0013752 ; wait for byte available
	RRC		; 03754 0001033 ; read byte, clear flag
	RAL	3	; 03755 0003003 ; shift byte into top of AC
	RAL	3	; 03756 0003003
	RAL	2	; 03757 0003002
	RSF		; 03760 0002040
	JMP	.-1	; 03761 0013760 ; wait for byte available
	RRC		; 03762 0001033 ; read into low byte of AC
	JMP	*rdword	; 03763 0113746

L03764			; 03764 0020000
L03765			; 03765 0001777
L03766			; 03766 0020000
			; 03767 0010000
			; 03770 0004005
			; 03771 0046000
			; 03772 0021777
			; 03773 0000000
			; 03774 0067766
hiaddr	DATA	0017702	; 03775 0017702
			; 03776 0010000
			; 03777 0177777
	END		;
