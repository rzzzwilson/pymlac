;;;;;;;;;;;;;;;;;;;;;;;;;
; check the AND instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; first, simple AND
	lac	minus1	;
	and	one	;
	sam	one	; -1 & 1 -> 1
	hlt		;
	law	010	;
	and	one	;
	sam	zero	; 010 & 1 -> 0
	hlt		;
	law	02	;
	and	two	;
	sam	two	; 02 & 2 -> 2
	hlt		;
	lac	minus1	; -1 & 0100000 -> 0100000
	and	hibit	;
	sam	hibit	;
	hlt		;
; now some indirect ANDs
	lac	minus1	;
	and	*indm1	;
	sam	minus1	;
	hlt		;
	lac	minus1	;
	and	*ind0	;
	sam	zero	;
	hlt		;
	hlt		;
			;
zero	data	0	;
one	data	1	;
two	data	2	;
minus1	data	0177777	;
indm1	data	minus1	;
ind0	data	zero	;
hibit	data	0100000	; just high bit
	end
