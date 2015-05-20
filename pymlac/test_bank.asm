;;;;;;;;;;;;;;;;;;;;;;;;;
; test the use of bank addresses
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
	lac	exp	; put value in high memory
	dac	*ihigha	;
	cla		;
	lac	*ihigha	;
	sam	exp
	hlt		;
	hlt		;
; data
ihigha	data	010000	;
exp	data	012345	;
	end
