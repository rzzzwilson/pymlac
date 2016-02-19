; test pseudo-ops
        org     0100

test    equ     045

start   hlt
        law     test

        org     0200

start2  nop

        org     0300

start3  nop
        bss     1
        hlt

str     asciiz  'str'
str2    asciiz  'str0'

str3    ascii   'str11'

dat     data    0
dat2    data    0177777

        end     start
;|$1   0000000
;|     0004000 + 045
;|$2   0100000
;|$3   0100000
;|$4   0000000          ; BSS behaves like 'org .+n'
;|     0071564          ; 'st'
;|     0071000          ; 'r\0'
;|     0071564          ; 'st'
;|     0071060          ; 'r0'
;|     0000000          ; zero byte
;|     0071564          ; 'rs'
;|     0071061          ; 't1'
;|     0030400          ; '1\0'
;|     0000000
;|     0177777
