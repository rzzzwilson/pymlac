; an assembler test file
        org     0100

test    equ     4
print   equ     0200        ; print subroutine address

start   law     test
        dac     save
        law     1
        add     save2
        dac     save2
        law     string
        jms     print
        hlt

save    bss     1
save2   data    3
string  ascii   'Test'
        data    0

        end     start
