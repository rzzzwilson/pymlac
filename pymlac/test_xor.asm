;;;;;;;;;;;;;;;;;;;;;;;;;
; check the XOR instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; first, simple XOR
	law	0	;
	xor	one	;
	sam	one	; 0 ^ 1 -> 1
	hlt		;
	law	1	;
	xor	one	;
	sam	zero	; 1 ^ 1 -> 0
	hlt		;
	law	1	;
	xor	zero	;
	sam	one	; 1 ^ 0 -> 1
	hlt		;
	lac	minus1	;
	xor	one	;
	sam	hbit0	; 0177777 ^ 1 -> 0177776
	hlt		;
; now some indirect XORs
	law	0	;
	xor	*indone	;
	sam	one	; 0 ^ 1 -> 1
	hlt		;
	law	1	;
	xor	*indone	;
	sam	zero	; 1 ^ 1 -> 0
	hlt		;
	law	1	;
	xor	*indzero;
	sam	one	; 1 ^ 0 -> 1
	hlt		;
	lac	minus1	;
	xor	*indone	;
	sam	hbit0	; 0177777 ^ 1 -> 0177776
	hlt		;
	hlt		;
; data for tests
zero	data	0	;
one	data	1	;
minus1	data	0177777	;
hbit	data	0100000	; just high bit
hbit0	data	0177776	; all set except bit 15
indzero	data	zero	;
indone	data	one	;
	end
