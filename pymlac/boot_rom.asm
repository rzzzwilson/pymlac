;-----------------------
; PTR ROM code
;-----------------------
        org     040
start   lac     base    ;40 get load address
        dac     010     ;41 put into auto-inc reg
        lwc     076     ;42 -0100+1 into AC
        dac     020     ;43 put into memory
        hon             ;44 start PTR
wait    cal             ;45 clear AC+LINK
        hsf             ;46 skip if PTR has data
        jmp     .-1     ;47 wait until is data
        hrb             ;50 read PTR -> AC
        sam     what    ;51 skip if AC == 2
        jmp     wait    ;52 wait until PTR return 0
loop    hsf             ;53 skip if PTR has data
        jmp     .-1     ;54 wait until is data
        hrb             ;55 read PTR -> AC
        ral     3       ;56 move byte into high AC
        ral     3       ;57
        ral     2       ;60
        hsn             ;61 wait until PTR moves
        jmp     .-1     ;62
        hsf             ;63 skip if PTR has data
        jmp     .-1     ;64 wait until is data
        hrb             ;65 read PTR -> AC
        dac     *010    ;66 store word, inc pointer
        hsn             ;67 wait until PTR moves
        jmp     .-1     ;70
        cal             ;71 clear AC & LINK
        isz     020     ;72 inc mem and skip zero
        jmp     loop    ;73 if not finished, jump
        jmp     *go     ;74 execute the blockloader
what    data    2       ;75
go      data    03700   ;76
base    data    03677   ;77

