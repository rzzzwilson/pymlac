;;;;;;;;;;;;;;;;;;;;;;;;;
; test ISZ instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; check simple ISZ
	lwc	2	; put -2 into ISZ target
	dac	isztest	;
	isz	isztest	; first ISZ, isztest <- -1,  no skip
	jmp	.+2	; 
	hlt		;
	isz	isztest	; second ISZ, isztest <- 0, skip
	hlt		;
; check indirect ISZ
	lwc	2	; put -2 into ISZ target
	dac	isztest	;
	isz	*indisz	; first ISZ, *indisz <- -1,  no skip
	jmp	.+2	; 
	hlt		;
	isz	*indisz	; second ISZ, *indisz <- 0, skip
	hlt		;
	hlt		;
; data for tests
isztest	data	0	;
indisz	data	isztest	;
	end
