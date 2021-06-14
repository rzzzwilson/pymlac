; a very simple 'smoke-test' file
        org     02

dot     equ     01

        org     0200

start   jmp     dot         ; test handling of fields with comment
        hlt

        end     start
