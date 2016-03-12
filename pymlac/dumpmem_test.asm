;-------------------------------
; Just loop in place - CPU speed test.
; Also has two blocks - blockloader test.
;-------------------------------
	org	0100		; 
start	nop                     ;
        jmp	other           ; 
                                ;
        org     0104            ;
other   law     0111            ;
        hlt                     ;
;-------------------------------
	end     start
