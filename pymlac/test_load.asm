;;;;;;;;;;;;;;;;;;;;;;;;;
; test the block loaderible
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
	cla		; clear AC
	lac	*t1	; load high mem indirectly
	sam	expt1	; skip is as expected
	hlt		;
	hlt		;
; data
t1	data	hit1	;
expt1	data	0123	;

	org	05000	; in high memory (> 11bit address)
hit1	data	0123	;
	end
