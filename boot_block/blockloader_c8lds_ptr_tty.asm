; 'c8lds' blockloader disassembled from chars.ptp.
;
; this loader is smart - it looks at the ROM code
; and decides if it should use PTR or TTY.

        ORG     03700   ;

cksum   equ     03677   ; store checksum just below start address

start	RCF		; 03700 0001032
	JMP	patch	; 03701 0013740 ; patch loadeer to use PTR or TTY
rdblok	DAC	cksum	; 03702 0023677 ; AC is zero at this point
skpzer	JMS	rdbyte	; 03703 0037760 ; wait for non-zero byte
	ASN		; 03704 0102001
	JMP	skpzer	; 03705 0013703
	CIA		; 03706 0100006
	DAC	wrdcnt	; 03707 0023777 ; save word count (or load address?)
	JMS	rdword	; 03710 0037750 ; get load address
	DAC	ldaddr	; 03711 0023776
	SAM	eolval	; 03712 0077730
	JMP	rddata	; 03713 0013715
	HLT		; 03714 0000000
rddata	JMS	rdword	; 03715 0037750
	DAC	*ldaddr	; 03716 0123776
	JMS	updcks	; 03717 0037731
	ISZ	ldaddr	; 03720 0033776
	ISZ	wrdcnt	; 03721 0033777
	JMP	rddata	; 03722 0013715
	JMS	rdword	; 03723 0037750
	SUB	cksum	; 03724 0073677
	ASN		; 03725 0102001
	JMP	nxtblk	; 03726 0013746
	HLT		; 03727 0000000

eolval	DATA	0177777	; 03730 0177777 ;' end-of-load' load address value

;------------------------
; Update checksum.  New word in AC.
; On exit, AC is updated checksum.
;------------------------
updcks	DATA	0	; 03731 0017720
	CLL		; 03732 0100010
	ADD	cksum	; 03733 0067677
	LSZ		; 03734 0002004
	IAC		; 03735 0100004
	DAC	cksum	; 03736 0023677
	JMP	*updcks	; 03737 0113731

;------------------------
; Patch loader to use TTY or PTR.
;------------------------
patch	HON		; 03740 0001061
	LAC	pattty	; 03741 0063774
	DAC	usetty	; 03742 0023761
	LAW	01032	; 03743 0005032 ; load RCF instruction
	SAM	*romflg	; 03744 0177775 ; skip if ROM is TTY (RCF @044)
	DAC	usetty	; 03745 0023761 ; patch this code to use PTR
nxtblk	CAL		; 03746 0100011
	JMP	rdblok	; 03747 0013702

;------------------------
; Read a word from the input device.
;------------------------
rdword	DATA	0	; 03750 0017711
	CAL		; 03751 0100011
	JMS	rdbyte	; 03752 0037760
	RAL	3	; 03753 0003003
	RAL	3	; 03754 0003003
	RAL	2	; 03755 0003002
	JMS	rdbyte	; 03756 0037760
	JMP	*rdword	; 03757 0113750

;------------------------
; Read a byte.  Patched to use TTY or PTR.
;------------------------
rdbyte	DATA	0	; 03760 0017757
usetty	RCF		; 03761 0001032
	HSN		; 03762 0102400
	JMP	.-1	; 03763 0013762
	HSF		; 03764 0002400
	JMP	.-1	; 03765 0013764
	HRB		; 03766 0001051
	JMP	*rdbyte	; 03767 0113760

rdtty	RSF		; 03770 0002040
	JMP	.-1	; 03771 0013770
	RRC		; 03772 0001033
	JMP	*rdbyte	; 03773 0113760

pattty	JMP	rdtty	; 03774 0013770
romflg	DATA	000044	; 03775 0000044
ldaddr	DATA	000000	; 03776 0000000
wrdcnt	DATA	000000	; 03777 0000000

	END		;
