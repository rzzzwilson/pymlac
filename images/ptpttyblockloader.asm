;------------------------
; This disassembled block loader was taken from 40tp_simpleDisplay.ptp.
;
; This block loader decides if it should load from papertape or TTY.
;------------------------
	org	17700	;
			;
cksum	equ	.-1	;
			;
	rcf		;
	jmp	patch	;
;------------------------
ndpatch	dac	cksum	;AC is zero here (patch side-effect)
	jms	rdbyte	;
	asn		;
	jmp	.-2	;wait here until no more zero bytes (have word count)
	cia		;
	dac	wrdcnt	;store neg word count
	jms	rdword	;read load address
	dac	ldaddr	;
	sam	neg1	;
	jmp	.+2	;
	hlt		;if load address is -1, halt
rdblock	jms	rdword	;now read block, storing words
	dac	*ldaddr	;
	jms	dosum	;
	isz	ldaddr	;
	isz	wrdcnt	;
	jmp	rdblock	;
	jms	rdword	;get checksum word
	sub	cksum	;compare with running checksum
	asn		;
	jmp	stblock	;if same, get next block
	hlt		;if not same, HALT
;------------------------
neg1	data	177777	;
;------------------------
; Subroutine to compute checksum.
; Word to sum is in AC, running checksum left in cksum.
;------------------------
dosum	data	0	;
	cll		;clear link in case of overflow
	add	cksum	;add running to AC
	lsz		;overflow? skip if so
	iac		;overflow!, bump running sum
	dac	cksum	;save running sum
	jmp	*dosum	;
;------------------------
; Code to decide what input device we are going to use.
; The decision is made by looking at address 0044 in the boot loader.
; If the instruction there is 001032 (rcf) then TTY input is patched.
;------------------------
patch	hon		;start PTR
	lac	ttyset	;get patch instruction (jmp rdtty)
	dac	devpat	;patch code
	law	1032	;check if addr 044 is rcf (TTY boot loader)
	sam	*adr044	;
	dac	devpat	;if not, put rcf *back*
stblock	cal		;clear AC
	jmp	ndpatch	;
;------------------------
; Subroutine to read a WORD from the input device.
; Word value left in AC.
;------------------------
rdword	data	0	;
	cal		;
	jms	rdbyte	;
	ral	3	;
	ral	3	;
	ral	2	;
	jms	rdbyte	;
	jmp	*rdword	;
;------------------------
; Subroutine to read a byte from the input device.
; Note - patched to use one of two input devices.
;------------------------
rdbyte	data	0	;
devpat	rcf		;clear TTY flag - could be patched to 'jmp rdtty'
	hsn		;wait for PTR to have data
	jmp	.-1	;
	hsf		;
	jmp	.-1	;
	hrb		;read PTR byte
	jmp	*rdbyte	;
			;
rdtty	rsf		;wait for TTY to have data
	jmp	.-1	;
	rrc		;read TTY byte and clear TTY flag
	jmp	*rdbyte	;
;------------------------
ttyset	jmp	rdtty	;
adr044	data	0044	;pointer to address 000044
;------------------------
ldaddr	equ	.	; address 3776
wrdcnt	equ	.+1	; address 3777
;------------------------
	end		;
