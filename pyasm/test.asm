; a test comment on the first line
        org     0100

start   law     10
        lac     start2      ; comment
        lac     .-2
;        lac     undef       ; another comment
        hlt

fred    equ     2           ; EQU

;        org     128 + 1
        org     . + 010

start2  
        lac     start + 2   ; comment
        nop
string  data    'ascii'
        hlt

        end     start
