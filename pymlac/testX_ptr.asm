;;;;;;;;;;;;;;;;;;;;;;;;;
; check the PTR instructions
; we assume a *.ptp file is mounted
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; turn on PTR, read 3 chars
	lwc	3	;
	dac	lcount	;
	hon		;
loop	hsf		;
	jmp	loop	;
	cla		;
	hrb		;
	nop		;
loop2	hsn		;
	jmp	loop2	;
	isz	lcount	;
	jmp	loop	;
	hof		;
	hlt		;
; data
lcount	data	0	;
	end
