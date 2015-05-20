;;;;;;;;;;;;;;;;;;;;;;;;;
; check LAC instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; check simple LAC
	lac	zero	; load AC with 0
	sam	zero	; check it's actually 0
	hlt		;
	lac	one	; load AC with 1
	sam	one	; check it's actually 1
	hlt		;
	lac	minus1	; load AC with -1 (0177777)
	sam	minus1	; check it's actually -1
	hlt		;
; check indirect LAC
	lac	*indzero; load AC with 0
	sam	zero	; check it's actually 0
	hlt		;
	lac	*indone	; load AC with 1
	sam	one	; check it's actually 1
	hlt		;
	lac	*indm1	; load AC with -1 (0177777)
	sam	minus1	; check it's actually -1
	hlt		;
	hlt		;
; data for tests
zero	data	0	;
one	data	1	;
minus1	data	0177777	;
indzero	data	zero	;
indone	data	one	;
indm1	data	minus1	;
	end
