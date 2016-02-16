; test the display processor opcodes
;**************************
; display processor orders (partial listing)
;**************************
        org     0100

        dlxa    0
        dlxa    1
        dlxa    01777
;|$1 0010000 + 0
;|   0010000 + 1
;|   0010000 + 01777
        dlya    0
        dlya    1
        dlya    01777
;|   0020000 + 0
;|   0020000 + 1
;|   0020000 + 01777
        inc     e,f
;|   0030171
        inc     e,d+3+3
        inc     d+2+1,b-3+2
        inc     b-2-2,b+0-3
        inc     b+2-1,b+3+2
        inc     d+0-2,b+0+3
        inc     b+0+3,B+0+3
        inc     f,f
;|   0030233
;|   0110772
;|   0173307
;|   0152732
;|   0103303
;|   0141703
;|   0074571
        inc     e,d+3+3
;|   0030233
        djms    0
        djms    1
        djms    01777
;|   0050000 + 0
;|   0050000 + 1
;|   0050000 + 01777
        djmp    0
        djmp    1
        djmp    01777
;|   0060000 + 0
;|   0060000 + 1
;|   0060000 + 01777
        dhlt
;|   0000000
        dnop
;|   0004000
        dsts    0
        dsts    1
        dsts    2
        dsts    3
;|   0004004
;|   0004005
;|   0004006
;|   0004007
        dstb    0
        dstb    1
        dstb    2
        dstb    3
;|   0004010
;|   0004011
;|   0004012
;|   0004013
        ddsp
;|   0004020
        dixm
        diym
;|   0005000
;|   0004400
        drjm
;|   0004040
        ddxm
        ddym
;|   0004200
;|   0004100
        dhvc
;|   0006000
        dopr    15
        dopr    14
;|   0004015
;|   0004014

        end
