;-------------------------------
; Test of display processor instructions 
; Display characters on screen.
;-------------------------------
	org	0100		; 
				;
	dof			; 
	law	dend		;
	dac	nddisp		;
	lwc	20		;
	dac	newscr		;
	lwc	40		; one second counter
	dac	count		; 
loop	ssf	 		; wait until 40 Hz sync is set
	jmp	.-1		; 
	scf	 		; clear 40Hz flag
	dsn 			; wait until display is off
	jmp	.-1		; 
	isz	count		;
	jmp	.+2		;
	jms	another		;
	law	display		; start display
	dla			; 
	don			; 
	jmp	loop		; keep going
;-------------------------------
hbit	data	0100000		; high bit mask
count	data	0		; 40Hz counter
char	data	040		; char to write
lchar	data	0177		; last char
idsts	dsts	0		; 
idlxa	dlxa	0		; 
idlya	dlya	0		; 
idjms	djms	dsub		;
idhlt	dhlt			;
idnop	dnop			;
incy	data	0020		;
curry	data	01740		;
nddisp	data	0		;start as dend
newscr	data	0		;
;-------------------------------
; Routine to add another line to display.
;-------------------------------
another	nop			;
	isz	newscr		;
	jmp	.+2		;
	jms	clear		;
	lwc	20		; half second counter
	dac	count		; 
	lac	curry		;
	sub	incy		;
	dac	curry		;
	lwc	1		;
	add	nddisp		;
	dac	010		;
	lac	idlxa		;
	dac	*010		;
	lac	idlya		;
	ior	curry		;
	dac	*010		;
	lac	idjms		;
	dac	*010		;
	lac	idhlt		;
	dac	*010		;
	law	3		;
	add	nddisp		;
	dac	nddisp		;
	jmp	*another	;
;-------------------------------
; Routine to clear the screen.
;-------------------------------
clear	nop			;
	lwc	20		;
	dac	newscr		;
	lac	idhlt		;
	dac	dend		;
	law	dend		;
	dac	nddisp		;
	law	01740		;
	dac	curry		;
	jmp	*clear		;
;-------------------------------
; Short vector characters
;-------------------------------
space	inc	e,F		; space
exclam	inc	e,D30		; !
	inc	B00,D02		; 
	inc	B03,02		; 
	inc	B02,F		; 
dquote	inc	E,D23		; "
	inc	03,B0-1		; 
	inc	-10,01		; 
	inc	13,D30		; 
	inc	B-1-3,0-1	; 
	inc	10,01		; 
	inc	F,F		; 
hash	inc	e,B13		; #
	inc	13,13		; 
	inc	D30,B-1-3	; 
	inc	-1-3,-1-3	; 
	inc	D23,B-30	; 
	inc	-30,D13		; 
	inc	B30,30		; 
	inc	F,F		; 
dollar	inc	e,D3-2		; $
	inc	B03,03		; 
	inc	03,03		; 
	inc	D3-2,B-30	; 
	inc	-3-2,3-2	; 
	inc	3-2,-3-2	; 
	inc	-30,F		; 
percent	inc	e,D20		; %
	inc	B13,21		; 
	inc	1-2,-2-1	; 
	inc	-12,02		; 
	inc	-12,-2-1	; 
	inc	1-2,21		; 
	inc	12,12		; 
	inc	F,F		; 
amp	inc	e,D30		; &
	inc	30,B-33		; 
	inc	-23,12		; 
	inc	10,1-2		; 
	inc	-2-2,-2-1	; 
	inc	0-2,2-1		; 
	inc	20,23		; 
	inc	F,F		; 
quote	inc	e,D23		; '
	inc	03,B0-1		; 
	inc	10,01		; 
	inc	-13,F		; 
lparen	inc	e,D30		; (
	inc	B-11,-12	; 
	inc	02,12		; 
	inc	11,F		; 
rparen	inc	e,D20		; )
	inc	B11,12		; 
	inc	02,-12		; 
	inc	-11,F		; 
star	inc	e,D03		; *
	inc	B32,32		; 
	inc	D-31,B0-3	; 
	inc	0-3,D31		; 
	inc	B-32,-32	; 
	inc	F,F		; 
plus	inc	e,D31		; +
	inc	B03,03		; 
	inc	D-3-3,B30	; 
	inc	30,F		; 
comma	inc	e,D2-2		; ,
	inc	B13,01		; 
	inc	-10,0-1		; 
	inc	F,F		; 
minus	inc	e,D13		; -
	inc	B30,30		; 
	inc	F,F		; 
dot	inc	e,D30		; .
	inc	B00,F		; 
slash	inc	e,D20		; /
	inc	B13,13		; 
	inc	13,F		; 
zero	inc	e,D12		; 0
	inc	B02,02		; 
	inc	22,2-2		; 
	inc	0-2,0-2		; 
	inc	-2-2,-22	; 
	inc	F,F		; 
one	inc	e,D10		; 1
	inc	B20,20		; 
	inc	D-20,B03	; 
	inc	03,02		; 
	inc	-2-2,F		; 
two	inc	e,D03		; 2
	inc	03,b22		; 
	inc	20,2-2		; 
	inc	-1-2,-2-1	; 
	inc	-3-3,30		; 
	inc	30,F		; 
three	inc	e,B30		; 3
	inc	32,-22		; 
	inc	-30,D30		; 
	inc	B22,-22		; 
	inc	-30,F		; 
four	inc	e,D30		; 4
	inc	10,B03		; 
	inc	03,02		; 
	inc	-3-3,-1-2	; 
	inc	30,30		; 
	inc	F,F		; 
five	inc	e,B30		; 5
	inc	31,02		; 
	inc	-32,-30		; 
	inc	03,30		; 
	inc	30,F		; 
six	inc	e,D03		; 6
	inc	B21,20		; 
	inc	2-2,-2-2	; 
	inc	-20,-22		; 
	inc	03,23		; 
	inc	20,2-2		; 
	inc	F,F		; 
seven	inc	e,B23		; 7
	inc	33,12		; 
	inc	-30,-30		; 
	inc	F,F		; 
eight	inc	e,D20		; 8
	inc	B20,21		; 
	inc	02,-31		; 
	inc	-32,22		; 
	inc	20,2-2		; 
	inc	-3-2,-3-1	; 
	inc	0-2,2-1		; 
	inc	F,F		; 
nine	inc	e,D2-1		; 9
	inc	B23,13		; 
	inc	03,-30		; 
	inc	-2-2,2-2	; 
	inc	20,F		; 
colon	inc	e,D32		; :
	inc	B00,D03		; 
	inc	01,B00		; 
	inc	F,F		; 
semcol	inc	e,D2-2		; ;
	inc	B13,01		; 
	inc	-10,10		; 
	inc	D03,01		; 
	inc	B-10,F		; 
lt	inc	e,D31		; <
	inc	30,B-21		; 
	inc	-21,-21		; 
	inc	21,21		; 
	inc	21,F		; 
equal	inc	e,D13		; =
	inc	B30,30		; 
	inc	D02,B-30	; 
	inc	-30,F		; 
gt	inc	e,D01		; >
	inc	B21,21		; 
	inc	21,-21		; 
	inc	-21,-21		; 
	inc	F,F		; 
query	inc	e,D30		; ?
	inc	B00,D02		; 
	inc	B02,22		; 
	inc	-12,-20		; 
	inc	-1-2,F		; 
at	inc	e,D30		; @
	inc	B-31,02		; 
	inc	02,22		; 
	inc	30,1-3		; 
	inc	-1-2,-30	; 
	inc	02,20		; 
	inc	0-2,F		; 
uppera	inc	e,B13		; A
	inc	13,12		; 
	inc	1-3,1-3		; 
	inc	1-2,D-23	; 
	inc	B-30,F		; 
upperb	inc	e,B03		; B
	inc	03,02		; 
	inc	30,2-1		; 
	inc	0-2,-2-1	; 
	inc	-30,D30		; 
	inc	B3-1,0-2	; 
	inc	-3-1,-30	; 
	inc	F,F		; 
upperc	inc	e,D32		; C
	inc	30,B-2-2	; 
	inc	-20,-22		; 
	inc	03,23		; 
	inc	20,2-2		; 
	inc	F,F		; 
upperd	inc	e,B03		; D
	inc	03,02		; 
	inc	30,2-1		; 
	inc	1-2,0-2		; 
	inc	-1-2,-2-1	; 
	inc	-30,F		; 
uppere	inc	e,B03		; E
	inc	03,02		; 
	inc	30,30		; 
	inc	D-1-2,-1-2	; 
	inc	B-20,-20	; 
	inc	D0-2,0-2	; 
	inc	B30,30		; 
	inc	F,F		; 
upperf	inc	e,B03		; F
	inc	02,30		; 
	inc	D-30,B03	; 
	inc	30,30		; 
	inc	F,F		; 
upperg	inc	e,D33		; G
	inc	B30,-1-3	; 
	inc	-30,-23		; 
	inc	03,32		; 
	inc	3-1,F		; 
upperh	inc	e,B03		; H
	inc	03,02		; 
	inc	D0-3,0-1	; 
	inc	B30,30		; 
	inc	Y,B03		; 
	inc	03,02		; 
	inc	Y,F		; 
upperi	inc	e,B30		; I
	inc	30,D-31		; 
	inc	B03,03		; 
	inc	D-31,B30	; 
	inc	30,F		; 
upperj	inc	e,D02		; J
	inc	B2-2,20		; 
	inc	22,03		; 
	inc	03,F		; 
upperk	inc	e,B03		; K
	inc	03,02		; 
	inc	D0-3,0-1	; 
	inc	B32,32		; 
	inc	Y,B-13		; 
	inc	-23,F		; 
upperl	inc	e,B03		; L
	inc	03,02		; 
	inc	Y,B30		; 
	inc	30,F		; 
upperm	inc	e,B03		; M
	inc	03,02		; 
	inc	3-3,33		; 
	inc	0-3,0-3		; 
	inc	0-2,F		; 
uppern	inc	e,B03		; N
	inc	03,02		; 
	inc	2-3,2-3		; 
	inc	2-2,03		; 
	inc	03,02		; 
	inc	F,F		; 
uppero	inc	e,D10		; O
	inc	B20,20		; 
	inc	13,02		; 
	inc	-13,-20		; 
	inc	-20,-1-3	; 
	inc	0-2,1-3		; 
	inc	F,F		; 
upperp	inc	e,B03		; P
	inc	03,02		; 
	inc	30,3-1		; 
	inc	0-2,-3-1	; 
	inc	-30,F		; 
upperq	inc	e,D10		; Q
	inc	B30,23		; 
	inc	03,-12		; 
	inc	-30,-2-3	; 
	inc	0-3,1-2		; 
	inc	D33,B3-3	; 
	inc	F,F		; 
upperr	inc	e,B03		; R
	inc	03,02		; 
	inc	30,3-1		; 
	inc	0-2,-3-1	; 
	inc	-30,D30		; 
	inc	B2-2,1-2	; 
	inc	F,F		; 
uppers	inc	e,D01		; S
	inc	B2-1,30		; 
	inc	13,-31		; 
	inc	-31,13		; 
	inc	30,2-1		; 
	inc	F,F		; 
uppert	inc	e,D30		; T
	inc	B03,03		; 
	inc	02,X		; 
	inc	B30,30		; 
	inc	F,F		; 
upperu	inc	e,D03		; U
	inc	03,02		; 
	inc	B0-3,0-3	; 
	inc	2-2,20		; 
	inc	22,03		; 
	inc	03,F		; 
upperv	inc	e,D03		; V
	inc	03,02		; 
	inc	B1-2,1-3	; 
	inc	1-3,12		; 
	inc	13,13		; 
	inc	F,F		; 
upperw	inc	e,B03		; W
	inc	03,02		; 
	inc	Y,B33		; 
	inc	3-3,03		; 
	inc	03,02		; 
	inc	F,F		; 
upperx	inc	e,B23		; X
	inc	22,23		; 
	inc	Y,B-23		; 
	inc	-22,-23		; 
	inc	F,F		; 
uppery	inc	e,D30		; Y
	inc	B02,03		; 
	inc	33,X		; 
	inc	B3-3,F		; 
upperz	inc	e,D30		; Z
	inc	30,B-30		; 
	inc	-30,23		; 
	inc	22,23		; 
	inc	-30,-30		; 
	inc	F,F		; 
lsquare	inc	e,D30		; [
	inc	10,B-20		; 
	inc	03,03		; 
	inc	02,20		; 
	inc	F,F		; 
slosh	inc	e,D30		; \
	inc	10,B-13		; 
	inc	-13,-12		; 
	inc	F,F		; 
rsquare	inc	e,D20		; ]
	inc	B20,03		; 
	inc	03,02		; 
	inc	-20,F		; 
hat	inc	e,D30		; ^
	inc	B03,03		; 
	inc	02,-1-2		; 
	inc	-2-2,31		; 
	inc	3-1,-22		; 
	inc	-12,F		; 
unders	inc	e,D-2-2		; _
	inc	B30,30		; 
	inc	20,20		; 
	inc	D-23,F		; 
bquote	inc	e,D13		; `
	inc	03,B-22		; 
	inc	D3-3,3-3	;
	inc	F,F		; 
lowera	inc	e,D03		; a
	inc	03,B30		; 
	inc	2-2,-1-3	; 
	inc	2-1,D-21	; 
	inc	B-3-1,-12	; 
	inc	21,20		; 
	inc	F,F		; 
lowerb	inc	e,B03		; b
	inc	03,03		; 
	inc	Y,D02		; 
	inc	B3-2,21		; 
	inc	03,-22		; 
	inc	-3-2,F		; 
lowerc	inc	e,D32		; c
	inc	20,B-2-2	; 
	inc	-20,-12		; 
	inc	02,22		; 
	inc	3-1,F		; 
lowerd	inc	e,D33		; d
	inc	21,B-32		; 
	inc	-2-2,0-3	; 
	inc	2-1,32		; 
	inc	d0-2,b03	; 
	inc	03,03		; 
	inc	F,F		; 
lowere	inc	e,D13		; e
	inc	B20,20		; 
	inc	-23,-20		; 
	inc	-1-2,0-3	; 
	inc	2-1,30		; 
	inc	F,F		; 
lowerf	inc	e,D20		; f
	inc	B03,03		; 
	inc	22,2-1		; 
	inc	D-1-2,B-30	; 
	inc	-20,F		; 
lowerg	inc	e,D0-2		; g
	inc	B3-1,22		; 
	inc	02,03		; 
	inc	-32,-2-2	; 
	inc	0-3,2-1		; 
	inc	32,F		; 
lowerh	inc	e,B03		; h
	inc	03,03		; 
	inc	D1-3,B20	; 
	inc	1-3,0-3		; 
	inc	F,F		; 
loweri	inc	e,D30		; i
	inc	B03,03		; 
	inc	D02,B00		; 
	inc	F,F		; 
lowerj	inc	e,B1-2		; j
	inc	20,12		; 
	inc	03,03		; 
	inc	D02,B00		; 
	inc	F,F		; 
lowerk	inc	e,B03		; k
	inc	03,03		; 
	inc	D3-2,B-3-3	; 
	inc	3-1,2-3		; 
	inc	F,F		; 
lowerl	inc	e,D30		; l
	inc	B-11,03		; 
	inc	02,02		; 
	inc	F,F		; 
lowerm	inc	e,B03		; m
	inc	03,D0-2		; 
	inc	B22,1-2		; 
	inc	22,1-2		; 
	inc	0-2,0-2		; 
	inc	D-30,B03	; 
	inc	F,F		; 
lowern	inc	e,B03		; n
	inc	03,D0-2		; 
	inc	B32,2-3		; 
	inc	0-3,F		; 
lowero	inc	e,D10		; o
	inc	B20,22		; 
	inc	02,-12		; 
	inc	-20,-2-2	; 
	inc	0-2,1-2		; 
	inc	F,F		; 
lowerp	inc	e,D0-2		; p
	inc	B03,03		; 
	inc	03,D0-1		; 
	inc	B30,1-2		; 
	inc	-1-2,-30	; 
	inc	F,F		; 
lowerq	inc	e,D32		; q
	inc	20,b-3-2	; 
	inc	-21,03		; 
	inc	22,3-2		; 
	inc	0-3,0-2		; 
	inc	0-2,A0173	; 
lowerr	inc	e,B03		; r
	inc	03,D0-3		; 
	inc	B22,31		; 
	inc	F,F		; 
lowers	inc	e,D01		; s
	inc	B3-1,22		; 
	inc	-21,-31		; 
	inc	22,3-1		; 
	inc	F,F		; 
lowert	inc	e,D30		; t
	inc	B-11,03		; 
	inc	02,02		; 
	inc	D-2-2,B20	; 
	inc	20,F		; 
loweru	inc	e,D03		; u
	inc	03,B0-2		; 
	inc	0-2,1-2		; 
	inc	20,22		; 
	inc	02,02		; 
	inc	Y,D02		; 
	inc	B1-2,F		; 
lowerv	inc	e,D03		; v
	inc	03,B2-3		; 
	inc	1-3,13		; 
	inc	13,F		; 
lowerw	inc	e,D03		; w
	inc	03,B1-3		; 
	inc	1-3,13		; 
	inc	1-3,1+3		; 
	inc	13,F		; 
lowerx	inc	e,B23		; x
	inc	33,D-20		; 
	inc	-30,B3-3	; 
	inc	2-3,F		; 
lowery	inc	e,D1-3		; y
	inc	B23,23		; 
	inc	03,X		; 
	inc	B1-3,2-3	; 
	inc	F,F		; 
lowerz	inc	e,B30		; z
	inc	20,A011		; 
	inc	B23,33		; 
	inc	-30,-20		; 
	inc	F,F		; 
lcurl	inc	e,D33		; {
	inc	03,B-20		;
	inc	1-3,-10		;
	inc	D10,B-1-3	;
	inc	20,F		;
pipe	inc	e,D33		; |
	inc	03,01		;
	inc	B0-3,D0-2	;
	inc	B0-3,A0173	;
rcurl	inc	e,D13		; }
	inc	03,B20		;
	inc	-1-3,10		;
	inc	D-10,B1-3	;
	inc	-20,F		;
tilde	inc	e,D03		; ~
	inc	B12,1-2		;
	inc	1-2,12		;
	inc	F,F		;
del	inc	e,B+0+3		; DEL (filled box)
	inc	B+0+3,B+1+0	;
	inc	B+0-3,B+0-3	;
	inc	B+1+0,B+0+3	;
	inc	B+0+3,B+1+0	;
	inc	B+0-3,B+0-3	;
	inc	B+1+0,B+0+3	;
	inc	B+0+3,F		;
cursn	inc	e,b03		; 
	inc	03,30		; 
	inc	30,0-3		; 
	inc	0-3,-30		; 
	inc	-30,d11		; 
	inc	b02,02		; 
	inc	20,20		; 
	inc	0-2,0-2		; 
	inc	-30,03		; 
	inc	20,0-2		; 
	inc	-10,01		; 
	inc	f,f		; 
curso	inc	e,b03		; 
	inc	03,30		; 
	inc	30,0-3		; 
	inc	0-3,-30		; 
	inc	-30,f		; 
newline	ddym			;
	dlxa	0		;
	drjm			;
;-------------------------------
; Display list subroutine - show all ASCII chars
;-------------------------------
dsub	djms	space		;
	djms	exclam		;
	djms	dquote		;
	djms	hash		;
	djms	dollar		;
	djms	percent		;
	djms	amp		;
	djms	quote		;
	djms	lparen		;
	djms	rparen		;
	djms	star		;
	djms	plus		;
	djms	comma		;
	djms	minus		;
	djms	dot		;
	djms	slash		;
	djms	zero		;
	djms	one		;
	djms	two		;
	djms	three		;
	djms	four		;
	djms	five		;
	djms	six		;
	djms	seven		;
	djms	eight		;
	djms	nine		;
	djms	colon		;
	djms	semcol		;
	djms	lt		;
	djms	equal		;
	djms	gt		;
	djms	query		;
	djms	at		;
;	djms	newline		;
	djms	lsquare		;
	djms	slosh		;
	djms	rsquare		;
	djms	hat		;
	djms	unders		;
	djms	bquote		;
	djms	lcurl		;
	djms	pipe		;
	djms	rcurl		;
	djms	tilde		;
	djms	del		;
	djms	curso		;
;	djms	newline		;
	djms	lowera		;
	djms	lowerb		;
	djms	lowerc		;
	djms	lowerd		;
	djms	lowere		;
	djms	lowerf		;
	djms	lowerg		;
	djms	lowerh		;
	djms	loweri		;
	djms	lowerj		;
	djms	lowerk		;
	djms	lowerl		;
	djms	lowerm		;
	djms	lowern		;
	djms	lowero		;
	djms	lowerp		;
	djms	lowerq		;
	djms	lowerr		;
	djms	lowers		;
	djms	lowert		;
	djms	loweru		;
	djms	lowerv		;
	djms	lowerw		;
	djms	lowerx		;
	djms	lowery		;
	djms	lowerz		;
;	djms	newline		;
	djms	uppera		;
	djms	upperb		;
	djms	upperc		;
	djms	upperd		;
	djms	uppere		;
	djms	upperf		;
	djms	upperg		;
	djms	upperh		;
	djms	upperi		;
	djms	upperj		;
	djms	upperk		;
	djms	upperl		;
	djms	upperm		;
	djms	uppern		;
	djms	uppero		;
	djms	upperp		;
	djms	upperq		;
	djms	upperr		;
	djms	uppers		;
	djms	uppert		;
	djms	upperu		;
	djms	upperv		;
	djms	upperw		;
	djms	upperx		;
	djms	uppery		;
	djms	upperz		;
	djms	cursn		;
;	djms	newline		;
	drjm			;
;-------------------------------
; Display list.  Dynamically added to every second.
;-------------------------------
display	dsts	1		; 
	dlxa	0		; 
	dlya	01740		; 
	djms	dsub		;
dend	dhlt			;
;-------------------------------
	end			;
