;;;;;;;;;;;;;;;;;;;;;;;;;
; test the increment registers (010 -> 017)
; indirect access through the inc registers
; increments the register and the new value is
; the effective address
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
	law	buff	;
	dac	010	; point 010 at 'buff'
	law	0123	;
	dac	*010	;
	lac	010	;
	sam	exp1	;
	hlt		;
	law	0123	;
	dac	*010	;
	lac	010	;
	sam	exp2	;
	hlt		;
	law	0123	;
	dac	*010	;
	lac	010	;
	sam	exp3	;
	hlt		;
; now check that value in first three addresses from 'buff'
	lac	buff1	;
	sam	exp	;
	hlt		;
	lac	buff2	;
	sam	exp	;
	hlt		;
	lac	buff3	;
	sam	exp	;
	hlt		;
	hlt		;
; data
exp	data	0123	;
exp1	data	buff1	;
exp2	data	buff2	;
exp3	data	buff3	;

	org	01000
buff	data	0	;
buff1	data	0	;
buff2	data	0	;
buff3	data	0	;
	end
