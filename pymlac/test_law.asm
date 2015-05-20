;;;;;;;;;;;;;;;;;;;;;;;;;
; check LAW instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; check simple LAW
	law	0	; load AC with 0
	sam	zero	; check it's actually 0
	hlt		;
	law	1	; load AC with 1
	sam	one	; check it's actually 1
	hlt		;
	law	2	; load AC with 2
	sam	two	; check it's actually 2
	hlt		;
	law	03777	; load AC with 11-bit ones
	sam	max	; check it's actually 03777
	hlt		;
	hlt		;
; data for tests
zero	data	0	;
one	data	1	;
two	data	2	;
max	data	03777	;
	end
