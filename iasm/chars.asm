;-------------------------------
; Test of display processor instructions 
; Display characters on screen.
;-------------------------------
	org	0100		; 
	dof			; 
loop	dsn 			; wait until display is off
	jmp	.-1		; 
	ssf	 		; wait until 40 Hz sync is set
	jmp	.-1		; 
	scf	 		; 
	lda	 		; get data switches
	and	hbit		; save only high bit (NOP or HLT)
	dac	.+1		; save and ...
	nop	 		;     execute
	law	dsub		; start display
	dla			; 
	don			; 
	jmp	loop		; keep going
hbit	data	0100000		; high bit mask
;-------------------------------
; Display list subroutine - show all ASCII chars
;-------------------------------
dsub	dsts	1		; 
	dlxa	020		; 
	dlya	0200		; 
	dsts	0		;
	djms	dlist0		;
	dlxa	020		; 
	dlya	0160		; 
	djms	dlist1		;
	dlxa	020		; 
	dlya	0140		; 
	djms	dlist2		;
	dlxa	020		; 
	dlya	0120		; 
	djms	dlist3		;
	dlxa	020		; 
	dlya	0100		; 
	djms	dlist4		;

	dsts	1		; 
	dlxa	020		; 
	dlya	0240		; 
	dsts	1		;
	djms	dlist0		;
	dlxa	020		; 
	dlya	0220		; 
	djms	dlist1		;
	dlxa	020		; 
	dlya	0200		; 
	djms	dlist2		;
	dlxa	020		; 
	dlya	0160		; 
	djms	dlist3		;
	dlxa	020		; 
	dlya	0140		; 
	djms	dlist4		;

	dsts	1		; 
	dlxa	020		; 
	dlya	0240		; 
	dsts	2		;
	djms	dlist0		;
	dlxa	020		; 
	dlya	0220		; 
	djms	dlist1		;
	dlxa	020		; 
	dlya	0200		; 
	djms	dlist2		;
	dlxa	020		; 
	dlya	0160		; 
	djms	dlist3		;
	dlxa	020		; 
	dlya	0140		; 
	djms	dlist4		;

	dsts	1		; 
	dlxa	020		; 
	dlya	0300		; 
	dsts	3		;
	djms	dlist0		;
	dlxa	020		; 
	dlya	0260		; 
	djms	dlist1		;
	dlxa	020		; 
	dlya	0240		; 
	djms	dlist2		;
	dlxa	020		; 
	dlya	0220		; 
	djms	dlist3		;
	dlxa	020		; 
	dlya	0200		; 
	djms	dlist4		;
	dhlt			; 
;-------------------------------
; Display list subroutine - show all ASCII chars
;-------------------------------
dlist0	djms	space		; space
	djms	exclam		; !
	djms	dquote		; "
	djms	hash		; #
	djms	dollar		; $
	djms	percent		; %
	djms	amp		; &
	djms	quote		; '
	djms	lparen		; (
	djms	rparen		; )
	djms	star		; *
	djms	plus		; +
	djms	comma		; ,
	djms	minus		; -
	djms	dot		; .
	djms	slash		; /
	drjm			; 
dlist1	djms	zero		; 0
	djms	one		; 1
	djms	two		; 2
	djms	three		; 3
	djms	four		; 4
	djms	five		; 5
	djms	six		; 6
	djms	seven		; 7
	djms	eight		; 8
	djms	nine		; 9
	djms	colon		; :
	djms	semcol		; ;
	djms	lt		; <
	djms	equal		; =
	djms	gt		; >
	djms	query		; ?
	djms	at		; @
	drjm			; 
dlist2	djms	uppera		; A
	djms	upperb		; B
	djms	upperc		; C
	djms	upperd		; D
	djms	uppere		; E
	djms	upperf		; F
	djms	upperg		; G
	djms	upperh		; H
	djms	upperi		; I
	djms	upperj		; J
	djms	upperk		; K
	djms	upperl		; L
	djms	upperm		; M
	djms	uppern		; N
	djms	uppero		; O
	djms	upperp		; P
	djms	upperq		; Q
	djms	upperr		; R
	djms	uppers		; S
	djms	uppert		; T
	djms	upperu		; U
	djms	upperv		; V
	djms	upperw		; W
	djms	upperx		; X
	djms	uppery		; Y
	djms	upperz		; Z
	djms	lsquare		; [
	djms	slosh		; \
	djms	rsquare		; ]
	djms	hat		; ^
	djms	unders		; _
	djms	bquote		; `
	drjm			; 
dlist3	djms	lowera		; a
	djms	lowerb		; b
	djms	lowerc		; c
	djms	lowerd		; d
	djms	lowere		; e
	djms	lowerf		; f
	djms	lowerg		; g
	djms	lowerh		; h
	djms	loweri		; i
	djms	lowerj		; j
	djms	lowerk		; k
	djms	lowerl		; l
	djms	lowerm		; m
	djms	lowern		; n
	djms	lowero		; o
	djms	lowerp		; p
	djms	lowerq		; q
	djms	lowerr		; r
	djms	lowers		; s
	djms	lowert		; t
	djms	loweru		; u
	djms	lowerv		; v
	djms	lowerw		; w
	djms	lowerx		; x
	djms	lowery		; y
	djms	lowerz		; z
	djms	lcurl		; {
	djms	pipe		; |
	djms	rcurl		; }
	djms	tilde		; ~
	djms	del		; DEL
	djms	cursn
	djms	curso
	djms	nl
	drjm			; 
dlist4	djms	uppert
	djms	lowerh
	djms	lowere
	djms	space
	djms	lowerq
	djms	loweru
	djms	loweri
	djms	lowerc
	djms	lowerk
	djms	space
	djms	lowerb
	djms	lowerr
	djms	lowero
	djms	lowerw
	djms	lowern
	djms	space
	djms	lowerf
	djms	lowero
	djms	lowerx
	djms	space
	djms	lowerj
	djms	loweru
	djms	lowerm
	djms	lowerp
	djms	lowers
	djms	space
	djms	lowero
	djms	lowerv
	djms	lowere
	djms	lowerr
	djms	space
	djms	lowert
	djms	lowerh
	djms	lowere
	djms	space
	djms	lowerl
	djms	lowera
	djms	lowerz
	djms	lowery
	djms	space
	djms	lowerd
	djms	lowero
	djms	lowerg
	djms	dot
	drjm
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
cursn	inc	e,b03		; cursor on
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
curso	inc	e,b03		; cursor off
	inc	03,30		; 
	inc	30,0-3		; 
	inc	0-3,-30		; 
	inc	-30,f		; 
nlx	inc	e,d12		; newline
	inc	b03,3-3		; 
	inc	03,d2-2		; 
	inc	b0-3,30		; 
	inc	f,f		; 
nl	inc	e,d12		; newline
	inc	b03,2-3		; 
	inc	03,d0-3		; 
	inc	b0-1,20		; 
	inc	d1-1,b03	; 
	inc	03,-30		; 
	inc	-30,0-3		; 
	inc	0-3,30		; 
	inc	30,f		; 
nl2	inc	e,d33		; newline
	inc	b0-2,-1-2	; 
	inc	-2-2,02		;
	inc	d0-2,b20	; 
	inc	f,f		; 
;-------------------------------
	end
