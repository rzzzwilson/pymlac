;;;;;;;;;;;;;;;;;;;;;;;;;
; check the microcoded instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; first, simple 'known' instructions
	lwc	1	;
	nop		; NOP - no change
	cla		; CLA - AC -> 0
	sam	zero	;
	hlt		;
	lwc	1	;
	cma		; CMA - AC -> 0
	sam	zero	;
	hlt		;
	cla		;
	cma		; CMA - AC -> 0177777
        sam	minus1	;
	hlt		;
	sta		; STA - AC -> 0177777
	sam	minus1	;
	hlt		;
	law	0	;
	iac		; IAC - AC -> 1
	sam	one	;
	hlt		;
	lwc	1	;
	iac		; IAC - AC -> 0, L complemented
	sam	zero	;
	hlt		;
	lwc	0	;
	coa		; COA - AC -> 1
	sam	one	;
	hlt		;
	cia		; CIA - AC -> 0177777
	sam	minus1	;
	hlt		;
	cll		; CLL - L -> 0
	lsz		; skip if link is zero
	hlt		;
	cml		; CML - L -> 1
	lsn		; skip if L not 0
	hlt		;
	cal		; CAL - AC->0, L->0
	sam	zero	;
	hlt		;
	lsz		; skip if link is zero
	hlt		;
	stl		; STL - L->1
	lsn		; skip if L not 0
	hlt		;
; now for some unknown compound instructions
	data	0100007	; clr AC, ~AC, ++AC
	sam	zero	; AC should be 0
	hlt		;
	hlt		;
; test ODA and LDA instrunction
;
;  DO THIS ONCE WE CAN RELIABLY SET DATA SWITCHES
;
; data for tests
zero	data	0	;
one	data	1	;
minus1	data	0177777	;
	end
