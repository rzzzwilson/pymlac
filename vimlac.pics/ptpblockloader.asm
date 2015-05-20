	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
	; Block loader from 40tp_simpleDisplay.ptp.
	; Reads from PTR or TTY depending on boot loader used.
	;
	; Format of one block on tape:
	;
	;	<wordcount byte>	1 byte
	;	<loadaddress word>	2 bytes
	;	<block words>		N words (from wordcount byte)
	;	<checksum word>		2 bytes
	;
	; The above is repeated until <loadaddress> is -1. Halts.
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
		org	177700	       ;
	chksum	equ	start-1	       ; checksum storage
                                       ;
001032	start	rcf		177700 ; 
013740	main	jmp	fixup	177701 ; go do PTR/TTY fixup
023677	rdblk	dac	chksum	177702 ; zero checksum
037760	zwait	jms	rbptr	177703 ; wait here until non-zero byte
102001		asn		177704 ; 
013703		jmp	zwait	177705 ; jump back if zero
100006		cia		177706 ; get block count BYTE, negate
023777		dac	numwds	177707 ;   and store in 'numwds'
037750		jms	rwptr	177710 ; get load address
023776		dac	ldaddr	177711 ; save it in 'ldaddr'
077730		sam	neg1	177712 ; skip if address == -1
013715		jmp	.+2	177713 ; 
000000		hlt		177714 ; halt here if negative load address
037750		jms	rwptr	177715 ; get block word
123776		dac	*ldaddr	177716 ; store it
037731		jms	dosum	177717 ; update checksum
033776		isz	ldaddr	177720 ; bump load address
033777		isz	numwds	177721 ; bump word counter
013715		jmp	lab2	177722 ; jump if block not finished
037750		jms	rwptr	177723 ; get block checksum
073677		sub	chksum	177724 ; check against expected checksum
102001		asn		177725 ; skip if checksum error
013746		jmp	next	177726 ; zero checksum and get next block
000000		hlt		177727 ; halt here if checksum error

177777	neg1	data	0177777	177730 ; 
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
	; Calculate checksum
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
017720	dosum	data	017720	177731 ; 
100010		cll		177732 ; 
067677		add	chksum	177733 ; checksum locn
002004		lsz		177734 ; 
100004		iac		177735 ; 
023677		dac	chksum	177736 ; checksum locn
113731		jmp	*dosum	177737 ; 
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
	; Look at boot loader code address 044.
	; If it's RCF then read from TTY, else use PTR.
	; Clear AC+Link then goto load block code.
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
001061	fixup	hon		177740 ; start PTR
063774		lac	ttyjmp	177741 ; (JMP 3770)
023761		dac	rbptr+1	177742 ; force read from TTY
005032		law	1032	177743 ; get RCF instruction into AC
177775		sam	*pt044	177744 ; if address 044 is RCF (ie TTY), skip
023761		dac	rbptr+1	177745 ; not TTY, put RCF back
100011	next	cal		177746 ; zero AC and Link
013702		jmp	rdblk	177747 ; go start reading block
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
	; Read a 16-bit word from PTR/TTY
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
017711	rwptr	data	017711	177750 ; read a word from papertape
100011		cal		177751 ; clear AC
037760		jms	rbptr	177752 ; read first byte
003003		ral	3	177753 ; shift it left 8 bits
003003		ral	3	177754 ;
003002		ral	2	177755 ;
037760		jms	rbptr	177756 ; add second byte
113750		jmp	*rwptr	177757 ; and return the word
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
	; Read an 8-bit byte from PTR/TTY
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
017757	rbptr	data	017757	177760 ; read a byte from PTR/TTY
001032		rcf		177761 ; becomes 'jmp 3770' if TTY
102400		hsn		177762 ; skip if PTR has no data
013762		jmp	.-1	177763 ; 
002400		hsf		177764 ; skip if PTR has data
013764		jmp	.-1	177765 ;   wait for byte here
001051		hrb		177766 ; read PTR - 'OR' into AC
113760		jmp	*rbptr	177767 ; 
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
	; TTY code - come here if TTY used
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
002040	rbtty	rsf		177770 ; wait until TTY has data
013770		jmp	.-1	177771 ; 
001033		rrc		177772 ; TTY clear & read
113760		jmp	*rbptr	177773 ; return
	;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
013770	ttyjmp	jmp	3770	177774 ; 
000044	pt044	data	000044	177775 ; point to 000044 (in boot loader)
000000	ldaddr	data 	0	177776 ; load address
000000	numwds	data 	0	177777 ; number of words in block

		end	start
