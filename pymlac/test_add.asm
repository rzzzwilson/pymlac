;;;;;;;;;;;;;;;;;;;;;;;;;
; check the ADD instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; first, simple ADD
	law	0	;
	add	zero	;
	sam	zero	; 0 + 0 -> 0
	hlt		;
	law	0	;
	add	one	;
	sam	one	; 0 + 1 -> 1
	hlt		;
	law	1	;
	add	one	;
	sam	two	; 1 + 1 -> 2
	hlt		;
	cll		;
	lwc	2	;
	add	one	;
	sam	minus1	; -2 + 1 -> -1
	hlt		;
	add	one	;
	sam	zero	; -1 + 1 -> -0
	hlt		;
; now some indirect ADDs
	law	0	;
	add	*indzero;
	sam	zero	; 0 + 0 -> 0
	hlt		;
	law	0	;
	add	*indone	;
	sam	one	; 0 + 1 -> 1
	hlt		;
	law	1	;
	add	*indone	;
	sam	two	; 1 + 1 -> 2
	hlt		;
	lwc	2	;
	add	*indone	;
	sam	minus1	; -2 + 1 -> -1
	hlt		;
	add	*indone	;
	sam	zero	; -1 + 1 -> -0
	hlt		;
	hlt		;
			;
zero	data	0	;
one	data	1	;
two	data	2	;
minus1	data	0177777	;
indone	data	one	;
indzero	data	zero	;
hibit	data	0100000	; just high bit
	end
