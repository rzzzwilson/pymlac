;-----------------------
; 'lc16sd' blockloader code
; disassembled from munch.ptp
;-----------------------
	org	03700	; addr  code

ldaddr	rcf		; 03700 0001032
numwrd	jms	.	; 03701 0037701 get address of 'chksum' into 'numwrd'

chksum	lac	numwrd	; 03702 0063701 are we are running in high memory (017700+)
	sam	himem	; 03703 0077775
	jmp	rdblk	; 03704 0013710 if not, just load tape

	lwc	012     ; 03705 0104012 else turn on the display
	dla		; 03706 0001003
	don		; 03707 0003100

rdblk	cal		; 03710 0100011 initialize block checksum
	dac	chksum	; 03711 0023702
	jms	rdword	; 03712 0037746 get load address
	dac	ldaddr	; 03713 0023700
	asp		; 03714 0002002 if high bit set
	jmp	ldend	; 03715 0013740 then end of tape load
	jms	rdword	; 03716 0037746 else get number of words in block
	dac	numwrd	; 03717 0023701
	jms	rdword	; 03720 0037746 read checksum word, add to checksum
blklp	jms	rdword	; 03721 0037746 get data word
	dac	*ldaddr	; 03722 0123700 store into memory
	lac	ldaddr	; 03723 0063700 get load address
	sar	3	; 03724 0003063 echo load address in display (if running)
	and	low10	; 03725 0047765
	ior	dlya0	; 03726 0053764
	dac	disp	; 03727 0023766
	lac	*ldaddr	; 03730 0163700 get last data word
	isz	ldaddr	; 03731 0033700 move 'load address' pointer
	isz	numwrd	; 03732 0033701 check end of block
	jmp	blklp	; 03733 0013721 jump if not ended
	add	chksum	; 03734 0067702 block end, check checksum
	asz		; 03735 0002001 if checksum invalid,
	jmp	.	; 03736 0013736     busy wait here
	jmp	rdblk	; 03737 0013710 else go get next block
; end of load, AC is load address, high bit set
ldend	dof		; 03740 0001012 turn off the display
	iac		; 03741 0100004
	asn		; 03742 0102001 if address is 0177777
	hlt		; 03743 0000000     then just halt
	jms	rdword	; 03744 0037746 else get AC contents
	jmp	*ldaddr	; 03745 0113700 and jump to start address
; read a word from tape, leave in AC
rdword	bss	1	; 03746 0000000
	add	chksum	; 03747 0067702
	dac	chksum	; 03750 0023702
	cal		; 03751 0100011
	rsf		; 03752 0002040
	jmp	.-1	; 03753 0013752
	rrc		; 03754 0001033
	ral	3	; 03755 0003003
	ral	3	; 03756 0003003
	ral	2	; 03757 0003002
	rsf		; 03760 0002040
	jmp	.-1	; 03761 0013760
	rrc		; 03762 0001033
	jmp	*rdword	; 03763 0113746

dlya0	dlya	0	; 03764 0020000
low10	data	001777	; 03765 0001777

; display routine, used if running in extended memory
disp	dlya	00000	; 03766 0020000
	dlxa	00000	; 03767 0010000
	dsts	1	; 03770 0004005
	data	0046000	;DLVH	02000	; 03771 0046000
	dlya	01777	; 03772 0021777
	dhlt		; 03773 0000000

	data	0067766	; 03774 0067766
himem	data	0017702	; 03775 0017702
	data	0010000	; 03776 0010000
	data	0177777	; 03777 0177777
	data	0000000	; 04000 0000000

	end		;
