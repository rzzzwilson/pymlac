;;;;;;;;;;;;;;;;;;;;;;;;;
; test DAC instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; check simple DAC
	lwc	1	; AC <- 0177777 (-1)
	dac	dactest	; store
	cla		; clear AC
	lac	dactest	; did we store -1?
	sam	minus1	; skip if so
	hlt		;
; check indirect DAC
	lwc	2	; AC <- 0177776 (-2)
	dac	*inddac	; store indirect to dactest
	cla		; clear AC
	lac	dactest	; did we store -2?
	sam	minus2	; skip if so
	hlt		;
	hlt		;
; data for tests
dactest	data	0	;
minus1	data	0177777	;
minus2	data	0177776	;
inddac	data	dactest	;
	end
