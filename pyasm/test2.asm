; a test comment on the first line
        org     0100

start   law     fred
        lac     *start2     ; comment
        lac     .-2
        hlt

fred    equ     2           ; EQU

        org     01100
start2  
        lac     start + 2   ; comment
offset  data    start - 3
        ascii   'xxxxxxxx'
        ascii   'xxxxxxx'
        ascii   "xx"
        ascii   'x'
tom     bss     4
end     hlt

        end     start
