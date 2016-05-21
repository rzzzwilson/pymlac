	org	0100

	dof		; turn display off
wdoff	dsn		;
	jmp	wdoff	; wait until display off
w40hz	ssf		;
	jmp	w40hz	; wait for 40Hz synch
	scf		; 
	law	hello	; start display
	dla		; 
	don		;
	jmp	wdoff	;

hbit	data	0100000

hello	dlxa	0400
	dlya	0400
	dsts	2
	dhvc
	djms	h
	djms	e
	djms	l
	djms	l
	djms	o
	dhlt

h	inc	e,b03
	inc	03,02
	inc	d30,30
	inc	b0-3,0-3
	inc	0-2,d03
	inc	01,b-30
	inc	-30,f

e	inc	e,b03
	inc	03,02
	inc	30,30
	inc	d-1-3,-1-1
	inc	b-30,-10
	inc	d0-3,0-1
	inc	b30,30
	inc	f,f

l	inc	e,b03
	inc	03,02
	inc	a1,p
	inc	30,30
	inc	f,f

o	inc	e,d02
	inc	b03,23
	inc	20,2-3
	inc	0-3,-2-2
	inc	-20,-22
	inc	f,f

	end
