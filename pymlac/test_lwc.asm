;;;;;;;;;;;;;;;;;;;;;;;;;
; check LWC instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; check simple LWC
	lwc	0	; load AC with complement of 0
	sam	zero	; check -0 is 0
	hlt		;
	lwc	1	; load AC with complement of 1
	sam	minus1	; check -1 is 0177777
	hlt		;
	lwc	2	; load AC with complement of 2
	sam	minus2	; check -2 is 0177776
	hlt		;
	lwc	03777	; load AC with complement of 03777
	sam	mmax	; check we have complement of 03777
	hlt		;
	hlt		;
; data for test
zero	data	0	;
minus1	data	0177777	;
minus2	data	0177776	;
mmax	data	0174001	;
	end
