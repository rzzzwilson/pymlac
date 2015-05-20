;;;;;;;;;;;;;;;;;;;;;;;;;
; check the SAM instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; first, simple SAM
	law	0	;
	sam	zero	; should skip
	hlt		;
	law	0	;
	sam	one	; should NOT skip
	jmp	.+2	;
	hlt		;
	lwc	1	;
	sam	minus1	; should skip
	hlt		;
	law	0	;
	sam	minus1	; should NOT skip
	jmp	.+2	;
	hlt		;
; now some indirect SAMs
	law	0	;
	sam	*indzero; should skip
	hlt		;
	law	0	;
	sam	*indone	; should NOT skip
	jmp	.+2	;
	hlt		;
	lwc	1	;
	sam	*indm1	; should skip
	hlt		;
	law	0	;
	sam	*indm1	; should NOT skip
	jmp	.+2	;
	hlt		;
	hlt		;
			;
zero	data	0	;
one	data	1	;
minus1	data	0177777	;
indone	data	one	;
indzero	data	zero	;
indm1	data	minus1	;
	end
