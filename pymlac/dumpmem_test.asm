;-------------------------------
; Just loop in place - CPU speed test.
;-------------------------------
	org	0100		; 
start	nop                     ;
        jmp	end             ; 
end     hlt                     ;
;-------------------------------
	end