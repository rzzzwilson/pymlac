; typed in from uppermemorytest.pdf

        org     0100

s       law     1           ; 0100
        dac     twd
s1      lac     twd
        ral     1
        dac     twd
        lwc     1
        dac     010010
l1      lac     twd
        dac     *010010     ; 0110
        cma
        dac     *010010
        lac     lit1
        sam     010010
        jmp     l1
        lwc     1
        dac     010010
l2      lac     twd        ; 0120
        sam     *010010
        jms     e
        cma
        sam     *010010
        jms     e
        lac     lit1
        sam     010010
        jmp     l2          ; 0130
        jmp     s1
e       bss     1
        dac     sav
        lac     010010
        hlt
        dac     tmp
        lac     *tmp
        hlt                 ; 0140
        lac     sav
        jmp     *e          ; 0142

#s2      bss     020

twd     data    0
sav     data    0
tmp     data    0
sva     data    0
svb     data    0
sve     data    0
svc     data    0
blm     data    0

lit1    data    007771
lit2    data    007776
lit3    data    010000
lit4    data    010006

        org     0163

p       lwc     1           ; 0163
        xam     *lit2
        dac     sva
        lac     lit2        ; (007776)
        dac     svb
        dac     sve         ; 0170
l4      dac     svb
        add     lit3        ; (010000)
        dac     svb
        cla
        xam     *svb
        dac     svc
        lac     *sve
        asm                 ; 0200
        jmp     l3
        lac     svc
        dac     *svb
        jmp     l4
l3      lac     sva
        dac     *lit2       ; (007776)
        lac     svb
        sub     lit4        ; 0210 (010006)
        dac     blm
        jmp     s

        rel     007714
        jmp     007400

        rel     007400
        hof
        jmp     *.+1
        zro     p       ; 010163

        rel     s2
        end
