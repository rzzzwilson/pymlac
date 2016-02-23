; blockloader from 40tp_simpleDisplay.ptp

cksum	equ	03677	; checksum stored at address 03677

	ORG	03700	; addr  code

     	RCF		; 03700 0001032
	JMP	start	; 03701 0013740
rdblock	DAC	cksum	; 03702 0023677
; skip zero bytes before block
      	JMS	rdbyte	; 03703 0037760
	ASN		; 03704 0102001
	JMP	.-2	; 03705 0013703
; AC is number of words in block, store negated number in 'numwrd'
	CIA		; 03706 0100006
	DAC	numwrd	; 03707 0023777
; read the block load address, store
	JMS	rdword	; 03710 0037750
	DAC	dot	; 03711 0023776
; if load addr is 0177777, load is finished
	SAM	negone	; 03712 0077730
	JMP	rddata	; 03713 0013715
	HLT		; 03714 0000000
; loop to read data words and store at 'dot'
rddata	JMS	rdword	; 03715 0037750
	DAC	*dot	; 03716 0123776
	JMS	docksm	; 03717 0037731
	ISZ	dot	; 03720 0033776
	ISZ	numwrd	; 03721 0033777
	JMP	rddata	; 03722 0013715
; data finished, read expected checksum and check validity
	JMS	rdword	; 03723 0037750
	SUB	cksum	; 03724 0073677
	ASN		; 03725 0102001
	JMP	nxtblk	; 03726 0013746
; halt if checksum error
	HLT		; 03727 0000000

negone	DATA	0177777	; 03730 0177777
docksm	DATA	0017720	; 03731 0017720
	CLL		; 03732 0100010
	ADD	cksum	; 03733 0067677
	LSZ		; 03734 0002004
	IAC		; 03735 0100004
	DAC	cksum	; 03736 0023677
	JMP	*docksm	; 03737 0113731

start	HON		; 03740 0001061
	LAC	L03774	; 03741 0063774
	DAC	patch1	; 03742 0023761
	LAW	01032	; 03743 0005032
	SAM	*L03775	; 03744 0177775
	DAC	patch1	; 03745 0023761
nxtblk	CAL		; 03746 0100011
	JMP	rdblock	; 03747 0013702

rdword	DATA	0017711	; 03750 0017711
	CAL		; 03751 0100011
	JMS	rdbyte	; 03752 0037760
	RAL	3	; 03753 0003003
	RAL	3	; 03754 0003003
	RAL	2	; 03755 0003002
	JMS	rdbyte	; 03756 0037760
	JMP	*rdword	; 03757 0113750

rdbyte	DATA	0017757	; 03760 0017757
patch1	RCF		; 03761 0001032
      	HSN		; 03762 0102400
	JMP	.-1   	; 03763 0013762
      	HSF		; 03764 0002400
	JMP	.-1	; 03765 0013764
	HRB		; 03766 0001051
	JMP	*rdbyte	; 03767 0113760
L03770	RSF		; 03770 0002040
	JMP	.-1	; 03771 0013770
	RRC		; 03772 0001033
	JMP	*rdbyte	; 03773 0113760

L03774	JMP	L03770	; 03774 0013770
L03775	DATA	000044	; 03775 0000044
dot	DATA	000000	; 03776 0000000
numwrd	DATA	000000	; 03777 0000000
	END		;
