
;------------------------------------------------------
; Paper tape block loader
;------------------------------------------------------
	org	7700

start	hon		;start PTR
	cal		;clear AC and LINK
	dac	sum	;zero checksum word
;------------------------
; Ignore leading zero chars.
;------------------------
zeros	jms	read1	;get one char
	asn		;if it's zero
	jmp	zeros	;  then go get another
;------------------------
; We now have a word count in AC.
;------------------------
	cia		;complement word count
	dac	words	;save word count
	jms	read2	;read 2 chars
	dac	addr	;save address to load to
	sam	k	;end code?
	jmp	bloop	;skip if not
	hlt		;  halt on end code - END OF LOAD
;------------------------
; Now read a block, saving at *addr.
;------------------------
bloop	jms	read2	;read 2 chars
	dac	*addr	;save at address and increment
	jms	dosum	;add to checksum
	isz	addr	;bump store address
	isz	words	;count words - skip if finished
	jmp	bloop	;loop for next word
	jms	read2	;read 2 chars
	sub	sum	;checksum word
	asn		;skip if checksum not zero
	jmp	.-25	;read another block
	hlt		;  CHECKSUM ERROR

k	word	177777	;end code

dosum	nop		;
	cll		;LINK <- 0
	add	sum	;add to checksum
	lsz		;if there was a carry
	iac		;  then wrap add to AC
	dac	sum	;store new checksum value
	jmp	dosums1	;return

L7740	hon
	cal
	jms	read1
	asz
	jmp	read2+3
	jmp	.-4
	jms	read2
h	asn
	hlt
	dac	addr
	jms	read2
	dac	*addr
	jmp	h-1
;------------------------
; Routine to read 2 8bit chars from PTR.
; 16 bits returned in AC.
;------------------------
read2	nop		;JMS save place
	cal		;clear AC+L
	jms	read1	;get first char
	ral	3	;
	ral	3	;
	ral	2	;move byte to high AC
	jms	read1	;get second byte
	jmp	*read2	;return char
;------------------------
; Routine to read one 8bit char from PTR.
; Returned in AC.
;------------------------
read1	nop		;
	hsn		;wait for char
	jmp	.-1	;  jump - not available
	hsf		;wait until char is past
	jmp	.-1	;  jump - still there
	hrb		;read PTR
	jmp	*read1	;return char
;------------------------
; Save places.
;------------------------
addr	nop		;address
sum	nop		;checksum word
words	nop		;word count

	end
