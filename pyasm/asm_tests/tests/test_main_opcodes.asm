; test the main processor opcodes
;**************************
; processor orders
;**************************
        org     0100

        law     0
        law     1
        law     03777
;|$1   0004000 + 0
;|     0004000 + 1
;|     0004000 + 03777
        lwc     0
        lwc     1
        lwc     03777
;|     0104000 + 0
;|     0104000 + 1
;|     0104000 + 03777
        jmp     0
        jmp     1
        jmp     03777
;|     0010000 + 0
;|     0010000 + 1
;|     0010000 + 03777
        jmp     *0
        jmp     *1
        jmp     *03777
;|     0110000 + 0
;|     0110000 + 1
;|     0110000 + 03777
        dac     0
        dac     1
        dac     03777
;|     0020000 + 0
;|     0020000 + 1
;|     0020000 + 03777
        dac     *0
        dac     *1
        dac     *03777
;|     0120000 + 0
;|     0120000 + 1
;|     0120000 + 03777
        xam     0
        xam     1
        xam     03777
;|     0024000 + 0
;|     0024000 + 1
;|     0024000 + 03777
        xam     *0
        xam     *1
        xam     *03777
;|     0124000 + 0
;|     0124000 + 1
;|     0124000 + 03777
        isz     0
        isz     1
        isz     03777
;|     0030000 + 0
;|     0030000 + 1
;|     0030000 + 03777
        isz     *0
        isz     *1
        isz     *03777
;|     0130000 + 0
;|     0130000 + 1
;|     0130000 + 03777
        jms     0
        jms     1
        jms     03777
;|     0034000 + 0
;|     0034000 + 1
;|     0034000 + 03777
        jms     *0
        jms     *1
        jms     *03777
;|     0134000 + 0
;|     0134000 + 1
;|     0134000 + 03777
        jms     0
        jms     1
        jms     03777
;|     0034000 + 0
;|     0034000 + 1
;|     0034000 + 03777
        jms     *0
        jms     *1
        jms     *03777
;|     0134000 + 0
;|     0134000 + 1
;|     0134000 + 03777
        and     0
        and     1
        and     03777
;|     0044000 + 0
;|     0044000 + 1
;|     0044000 + 03777
        and     *0
        and     *1
        and     *03777
;|     0144000 + 0
;|     0144000 + 1
;|     0144000 + 03777
        ior     0
        ior     1
        ior     03777
;|     0050000 + 0
;|     0050000 + 1
;|     0050000 + 03777
        ior     *0
        ior     *1
        ior     *03777
;|     0150000 + 0
;|     0150000 + 1
;|     0150000 + 03777
        xor     0
        xor     1
        xor     03777
;|     0054000 + 0
;|     0054000 + 1
;|     0054000 + 03777
        xor     *0
        xor     *1
        xor     *03777
;|     0154000 + 0
;|     0154000 + 1
;|     0154000 + 03777
        lac     0
        lac     1
        lac     03777
;|     0060000 + 0
;|     0060000 + 1
;|     0060000 + 03777
        lac     *0
        lac     *1
        lac     *03777
;|     0160000 + 0
;|     0160000 + 1
;|     0160000 + 03777
        add     0
        add     1
        add     03777
;|     0064000 + 0
;|     0064000 + 1
;|     0064000 + 03777
        add     *0
        add     *1
        add     *03777
;|     0164000 + 0
;|     0164000 + 1
;|     0164000 + 03777
        sub     0
        sub     1
        sub     03777
;|     0070000 + 0
;|     0070000 + 1
;|     0070000 + 03777
        sub     *0
        sub     *1
        sub     *03777
;|     0170000 + 0
;|     0170000 + 1
;|     0170000 + 03777
        sam     0
        sam     1
        sam     03777
;|     0074000 + 0
;|     0074000 + 1
;|     0074000 + 03777
        sam     *0
        sam     *1
        sam     *03777
;|     0174000 + 0
;|     0174000 + 1
;|     0174000 + 03777

;**************************
; operate instructions, class 1 (manipulative)
;**************************
        hlt     0
        hlt     1
        hlt     03777
;|     0000000 + 0
;|     0000000 + 1
;|     0000000 + 03777
        nop
;|     0100000
        cla
;|     0100001
        cma
;|     0100002
        sta
;|     0100003
        iac
;|     0100004
        coa
;|     0100005
        cia
;|     0100006
        cll
;|     0100010
        cml
;|     0100020
        stl
;|     0100030
        oda
;|     0100040
        lda
;|     0100041
        cal
;|     0100011

;**************************
; operate instructions, class 2 (shift & rotate)
;**************************
        ral     0
        ral     1
        ral     2
        ral     3
;|     0003000 + 0
;|     0003000 + 1
;|     0003000 + 2
;|     0003000 + 3
        rar     0
        rar     1
        rar     2
        rar     3
;|     0003020 + 0
;|     0003020 + 1
;|     0003020 + 2
;|     0003020 + 3
        sal     0
        sal     1
        sal     2
        sal     3
;|     0003040 + 0
;|     0003040 + 1
;|     0003040 + 2
;|     0003040 + 3
        sar     0
        sar     1
        sar     2
        sar     3
;|     0003060 + 0
;|     0003060 + 1
;|     0003060 + 2
;|     0003060 + 3
        don
;|     0003100

;**************************
; operate instructions, class 3 (conditional skip)
;**************************
        asz
;|     0002001
        asn
;|     0102001
        asp
;|     0002002
        asm
;|     0102002
        lsz
;|     0002004
        lsn
;|     0102004
        dsf
;|     0002010
        dsn
;|     0102010
        ksf
;|     0002020
        ksn
;|     0102020
        rsf
;|     0002040
        rsn
;|     0102040
        tsf
;|     0002100
        tsn
;|     0102100
        ssf
;|     0002200
        ssn
;|     0102200
        hsf
;|     0002400
        hsn
;|     0102400

;**************************
; iot (partial listing)
;**************************
        dla
;|     0001003
        ctb
;|     0001011
        dof
;|     0001012
        krb
;|     0001021
        kcf
;|     0001022
        krc
;|     0001023
        rrb
;|     0001031
        rcf
;|     0001032
        rrc
;|     0001033
        tpr
;|     0001041
        tcf
;|     0001042
        tpc
;|     0001043
        hrb
;|     0001051
        hof
;|     0001052
        hon
;|     0001061
        stb
;|     0001062
        scf
;|     0001071
        ios
;|     0001072
        iot 0101
;|     0001101
        iot 0111
;|     0001111
        iot 0131
;|     0001131
        iot 0132
;|     0001132
        iot 0134
;|     0001134
        iot 0141
;|     0001141
        iof
;|     0001161
        ion
;|     0001162
        pun
;|     0001271
        psf
;|     0001274

        end
