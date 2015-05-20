;;;;;;;;;;;;;;;;;;;;;;;;;
; check the IOR instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; first, simple IOR
	law	0	;
	ior	one	;
	sam	one	; 0 | 1 -> 1
	hlt		;
	law	1	;
	ior	zero	;
	sam	one	; 1 | 0 -> 1
	hlt		;
	lac	hbit	;
	ior	one	;
	sam	hbit1	; 0100000 | 1 -> 0100001
	hlt		;
	lwc 1	;
	ior	hamask	;
	sam	hares	;
	hlt		;
	lwc 1	;
	ior	lamask	;
	sam	lares	;
	hlt		;
	law	0	;
	ior	hamask	;
	sam	hamask	;
	hlt		;
	law	0	;
	ior	lamask	;
	sam	lamask	;
	hlt		;
; now some indirect IORs
	law	0	;
	ior	*indone	;
	sam	one	; 0 | 1 -> 1
	hlt		;
	law	1	;
	ior	*indzero;
	sam	one	; 1 | 0 -> 1
	hlt		;
	lac	hbit	;
	ior	*indone	;
	sam	hbit1	; 0100000 | 1 -> 0100001
	hlt		;
	lwc	1   ;
	ior	*indham	;
	sam	hares	;
	hlt		;
	lwc 1	;
	ior	*indlam	;
	sam	lares	;
	hlt		;
	law	0	;
	ior	*indham	;
	sam	hamask	;
	hlt		;
	law	0	;
	ior	*indlam	;
	sam	lamask	;
	hlt		;
	hlt		;
; data for tests
zero	data	0	;
one	data	1	;
hbit	data	0100000	; just high bit
hbit1	data	0100001	; high bit plus 1
hamask	data	0125252	; 1010101010101010
lamask	data	0052525	; 0101010101010101
hares	data	0177777 ; 1111111111111111
lares	data	0177777 ; 1111111111111111
indzero	data	zero	;
indone	data	one	;
indham	data	hamask	;
indlam	data	lamask	;
	end