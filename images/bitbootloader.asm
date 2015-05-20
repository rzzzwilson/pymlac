;-------------------------------
; Special TTY block loader.
; Disassembled from the 'snarf' tape.
;-------------------------------
	org	037700		; 
rdblock	rcf			; 
	cal			; 
	dac	chksum		; 
	dac	wordin		; 
	jms	rdnyb		; read block count (8 bits)
	jms	rdnyb		; 
	cia			; 
	dac	blkcnt		; 
	jms	rdword		; get block load address
	dac	ldaddr		; 
	sam	neg1		; if load address is 0177777
	jmp	.+2		; 
	hlt			;    then halt here
doblock	jms	rdword		; get next block word
	dac	*ldaddr		; store it
	jmp	dosum		; go do checksum
doincs	isz	ldaddr		; 
	isz	blkcnt		; 
	jmp	doblock		; 
	jms	rdword		; read block checksum
	sam	chksum		; same as expected?
	jmp	.+2		; 
	jmp	rdblock		;    jump if so
	hlt			; else halt here
dosum	cll			; accum AC to running checksum
	add	chksum		; 
	lsz			; handle overflow
	iac			; 
	dac	chksum		; 
	jmp	doincs		; 
;-------------------------------
; Read a word from TTY.
; Word read left in 'wordin' and AC.
;-------------------------------
rdword	hlt			; 
	cal			; 
	dac	wordin		; 
	jms	rdnyb		; 
	jms	rdnyb		; 
	jms	rdnyb		; 
	jms	rdnyb		; 
	jmp	*rdword		; 
;-------------------------------
; Read a nybble from TTY.
; Accumulates word in 'wordin'.
; Current 'wordin' value left in AC.
;-------------------------------
rdnyb	hlt			; 
wnyb	rsf			; wait here for TTY
	jmp	.-1		; 
	cal			; 
	rrc			; get TTY char
	dac	charin		; 
	and	chmask		; OK?
	sam	cheq		; 
	jmp	wnyb		; jum if not, keep waiting
	law	0017		; get low 4 bits
	and	charin		; 
	xam	wordin		; accumulate into 'wordin'
	ral	3		; 
	ral	1		; 
	ior	wordin		; 
	dac	wordin		; 
	jmp	*rdnyb		; 
;-------------------------------
neg1	data	0177777		; 
chmask	data	0160		; 
cheq	data	0100		; 
charin	data	0		; 
ldaddr	data	0		; 
blkcnt	data	0		; 
wordin	data	0		; 
	data	0		; unused?
chksum	data	0		; 
;-------------------------------
	end			; 
