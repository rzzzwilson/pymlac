;;;;;;;;;;;;;;;;;;;;;;;;;
; test the conditional skip instructions
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; check ASZ - skip if AC is zero
	lwc	1	; AC <- 0177777 (-1)
	asz		; should not skip
	jmp	.+2	;
	hlt		;
	law	0	;
	asz		; should skip
	hlt		;

; check ASN - skip if AC is not zero
	lwc	1	; AC <- 0177777 (-1)
	asn		; should skip
	hlt		;
	law	0	;
	asn		; should not skip
	jmp	.+2	;
	hlt		;

; check ASP - skip if AC is a positive number
; zero is positive here, as the test is for bit 0 set
	law	0	; AC <- 0
	asp		; should skip
	hlt		;
	law	1	; AC <- 1
	asp		; should skip
	hlt		;
	lwc	1	;
	asp		; should not skip
	jmp	.+2	;
	hlt		;

; check ASM - skip if AC is a negative number
; zero is positive here, as the test is for bit 0 set
	law	0	; AC <- 0
	asm		; should not skip
	jmp	.+2	;
	hlt		;
	law	1	; AC <- 1
	asm		; should not skip
	jmp	.+2	;
	hlt		;
	lwc	1	;
	asm		; should skip
	hlt		;

; check LSZ - skip if L is zero
	stl		; L <- 1
	lsz		; should not skip
	jmp	.+2	;
	hlt		;
	cll		; L <- 0
	lsz		; should skip
	hlt		;

; check LSN - skip if L is not zero
	stl		; L <- 1
	lsn		; should skip
	hlt		;
	cll		; L <- 0
	lsn		; should not skip
	jmp	.+2	;
	hlt		;

; can't easily test DSF, DSN, KSF, KSN, RSF, RSN,
; TSF, TSN, SSF, SSN, HSF, HSN as they test hardware

	hlt		;
	end
