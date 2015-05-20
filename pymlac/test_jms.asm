;;;;;;;;;;;;;;;;;;;;;;;;;
; test JMS instruction
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; check simple JMS
	jms	jmstest	; call test, AC contains return address
here	sam	retadr	; skip if so
	hlt		;
	lac	jmstest	; make sure saved return address is correct
	sam	retadr	;
	hlt		;
; check indirect JMS
test2	jms	*indjms	; call same test, AC=return address
here2	sam	retadr2	; skip if so
	hlt		;
	lac	jmstest	; make sure saved return address is correct
	sam	retadr2	;
	hlt		;
	hlt		;
; test routine for JMS - returns return address
jmstest	data	0	;
	lac	jmstest	; return with AC holding return address
	jmp	*jmstest;
; data for tests
retadr	data	here	;
retadr2	data	here2	;
indjms	data	jmstest	;
	end
