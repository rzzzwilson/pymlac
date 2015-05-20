;;;;;;;;;;;;;;;;;;;;;;;;;
; test XAM instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; check simple XAM
	stl		; L <- 1
	law	0	;
	dac	xamtest	;
	lwc	1	; AC <- 0177777 (-1)
	xam	xamtest	; switch with xamtest
	sam	zero	; test AC is 0
	hlt		;
	lsn		; L should still be 1
	hlt		;
	lwc	1	; check xamtest is -1
	sam	xamtest	;
	hlt		;
; check indirect XAM
	cll		; L <- 0
	law	0	;
	dac	xamtest	;
	lwc	1	; AC <- 0177777 (-1)
	xam	*indxam	; switch with xamtest (indirect)
	sam	zero	; test AC is 0
	hlt		;
	lsz		; L is still 0?
	hlt		;
	lwc	1	; check xamtest is -1
	sam	xamtest	;
	hlt		;
	hlt		;
; data for tests
xamtest	data	0	;
zero	data	0	;
indxam	data	xamtest	;
	end
