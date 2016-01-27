; a test comment on the first line
        org     0100

start   law     10
        lac     start2      ; comment
        lac     .-2
        hlt

fred    equ     2           ; EQU

        org     . + 010
start2  
        lac     start + 2   ; comment
string  data    'ascii'
end     hlt

        end     start
