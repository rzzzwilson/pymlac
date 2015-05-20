;;;;;;;;;;;;;;;;;;;;;;;;;
; test the JMP instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; check simple JMP
	jmp	jtest	;
	hlt		;
jtest	nop		;
; now test jump backwards
	jmp	j1	;
j0	jmp	j2	;
	hlt		;
j1	jmp	j0	;
	hlt		;
j2	nop		;
; now test indirect JMP
	jmp	*indjmp	;
	hlt		;
target	hlt		;
; data for test
indjmp	data	target	;
	end
