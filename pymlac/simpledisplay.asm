        org    0100

        dof             ; turn display off
wdoff   dsn             ;
        jmp    wdoff    ; wait until display off
w40hz   ssf             ;
        jmp    w40hz    ; wait for 40Hz synch
        scf             ; 
        law    hello    ; start display
        dla             ; 
        don             ;
        jmp    wdoff    ;

hbit    data    0100000

hello   dlxa    0400
        dlya    0400
        dsts    2
        dhvc
        djms    upperh
        djms    uppere
        djms    upperl
        djms    upperl
        djms    uppero
        dhlt

upperh  inc    e,b03           ; H
        inc    03,02           ; 
        inc    d0-3,0-1        ; 
        inc    b30,30          ; 
        inc    Y,b03           ; 
        inc    03,02           ; 
        inc    Y,f             ; 

uppere  inc    e,b03           ; E
        inc    03,02           ; 
        inc    30,30           ; 
        inc    d-1-2,-1-2      ; 
        inc    b-20,-20        ; 
        inc    d0-2,0-2        ; 
        inc    b30,30          ; 
        inc    f,f             ; 

upperl  inc    e,b03           ; L
        inc    03,02           ; 
        inc    Y,b30           ; 
        inc    30,f            ; 

uppero  inc    e,d10           ; O
        inc    b20,20          ; 
        inc    13,02           ; 
        inc    -13,-20         ; 
        inc    -20,-1-3        ; 
        inc    0-2,1-3         ; 
        inc    f,f             ; 

        end
