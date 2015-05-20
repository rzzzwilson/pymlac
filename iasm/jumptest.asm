; test some jump instructions
	org	0100	;
			;
	jmp	.+1	; pc-relative
	jmp	j	; to label
	hlt	01	; shouldn't get here
j	jmp	*l	; indirect
	hlt	02	; shouldn't get here
l	data	0200	; indirect target
			;
	org	0200	;
	jmp	l0300	; jump to label in another block
	hlt	03	; shouldn't get here
			;
	org	0300	;
l0300	hlt		; should stop here
			;
	end
