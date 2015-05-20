;;;;;;;;;;;;;;;;;;;;;;;;;
; check the SUB instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; first, simple SUB
	law	0	;
	sub	zero	;
	sam	zero	; 0 - 0 -> 0
	hlt		;
	law	1	;
	sub	zero	;
	sam	one	; 1 - 0 -> 1
	hlt		;
	law	1	;
	sub	one	;
	sam	zero	; 1 - 1 -> 0
	hlt		;
	cll		; L <- 0
	law	0	;
	sub	one	;
	sam	minus1	; 0 - 1 -> -1
	hlt		;
	lsn		; link should be 1
	hlt		;
	stl		; L <- 1
	law	0	;
	sub	one	;
	sam	minus1	; 0 - 1 -> -1
	hlt		;
	lsz		; link should be 0
	hlt		;
; now some indirect SUBs
	law	0	;
	sub	*indzero;
	sam	zero	; 0 - 0 -> 0
	hlt		;
	law	1	;
	sub	*indzero;
	sam	one	; 1 - 0 -> 1
	hlt		;
	law	1	;
	sub	*indone	;
	sam	zero	; 1 - 1 -> 0
	hlt		;
	cll		; L <- 0
	law	0	;
	sub	*indone	;
	sam	minus1	; 0 - 1 -> -1
	hlt		;
	lsn		; link should be 1
	hlt		;
	stl		; L <- 1
	law	0	;
	sub	*indone	;
	sam	minus1	; 0 - 1 -> -1
	hlt		;
	lsz		; link should be 0
	hlt		;
	hlt		;
			;
zero	data	0	;
one	data	1	;
minus1	data	0177777	;
indone	data	one	;
indzero	data	zero	;
	end
