;-------------------------------
; Test of display processor instructions 
; Display characters on screen.
;-------------------------------
        org     0100           ; 
        dof                    ; 
loop    dsn                    ; wait until display is off
        jmp     loop           ; 
;        ssf                    ; wait until 40 Hz sync is set
;        jmp     .-1            ; 
;        scf                    ; 
;        lda                    ; get data switches
;        and     hbit           ; save only high bit (NOP or HLT)
;        dac     .+1            ; save and ...
;        nop                    ;     execute
        law     dsub           ; start display
        dla                    ; 
        don                    ; 
;        hlt                    ; DEBUG
        jmp     loop           ; keep going
;hbit    data    0100000        ; high bit mask
;-------------------------------
; Display list subroutine - show all ASCII chars
;-------------------------------
dsub 
;         dsts    1              ;
         dsts    2              ;
         dhvc                   ;
         dlxa    004            ;
         dlya    0400           ;
         djms    dlist0         ;
         dlxa    0004            ; 
         dlya    0340           ; 
         djms    dlist1         ;
         dlxa    0004           ; 
         dlya    0300           ; 
         djms    dlist2         ;
         dlxa    0004           ; 
         dlya    0240           ; 
         djms    dlist3         ;
;         dlxa    0004           ; 
;         dlya    0200           ; 
;         djms    dlist4         ;

;        dsts    1              ; 
;        dlxa    020            ; 
;        dlya    0240           ; 
;        dsts    1              ; 
;        djms    dlist0         ;
;        dlxa    020            ; 
;        dlya    0220           ; 
;        djms    dlist1         ;
;        dlxa    020            ; 
;        dlya    0200           ; 
;        djms    dlist2         ;
;        dlxa    020            ; 
;        dlya    0160           ; 
;        djms    dlist3         ;
;        dlxa    020            ; 
;        dlya    0140           ; 
;        djms    dlist4         ;
;
;        dsts    1              ; 
;        dlxa    020            ; 
;        dlya    0240           ; 
;        dsts    2              ; 
;        djms    dlist0         ;
;        dlxa    020            ; 
;        dlya    0220           ; 
;        djms    dlist1         ;
;        dlxa    020            ; 
;        dlya    0200           ; 
;        djms    dlist2         ;
;        dlxa    020            ; 
;        dlya    0160           ; 
;        djms    dlist3         ;
;        dlxa    020            ; 
;        dlya    0140           ; 
;        djms    dlist4         ;

;        dsts    1              ; 
;        dlxa    020            ; 
;        dlya    0300           ; 
;        dsts    3              ;
;        djms    dlist0         ;
;        dlxa    020            ; 
;        dlya    0260           ; 
;        djms    dlist1         ;
;        dlxa    020            ; 
;        dlya    0240           ; 
;        djms    dlist2         ;
;        dlxa    020            ; 
;        dlya    0220           ; 
;        djms    dlist3         ;
;        dlxa    020            ; 
;        dlya    0200           ; 
;        djms    dlist4         ;
        dhlt                   ; 
;-------------------------------
; Display list subroutine - show all ASCII chars
;-------------------------------
dlist0                         ;
        djms    space          ; space
        djms    exclam         ; !
        djms    dquote         ; "
        djms    hash           ; #
        djms    dollar         ; $
        djms    percent        ; %
        djms    amp            ; &
        djms    quote          ; '
        djms    lparen         ; (
        djms    rparen         ; )
        djms    star           ; *
        djms    plus           ; +
        djms    comma          ; ,
        djms    minus          ; -
        djms    dot            ; .
        djms    slash          ; /
        drjm                   ; 
dlist1                         ;
        djms    zero           ; 0
        djms    one            ; 1
        djms    two            ; 2
        djms    three          ; 3
        djms    four           ; 4
        djms    five           ; 5
        djms    six            ; 6
        djms    seven          ; 7
        djms    eight          ; 8
        djms    nine           ; 9
        djms    colon          ; :
        djms    semcol         ; ;
        djms    lt             ; <
        djms    equal          ; =
        djms    gt             ; >
        djms    query          ; ?
        djms    at             ; @
        drjm                   ; 
dlist2  djms    uppera         ; A
        djms    upperb         ; B
        djms    upperc         ; C
        djms    upperd         ; D
        djms    uppere         ; E
        djms    upperf         ; F
        djms    upperg         ; G
        djms    upperh         ; H
        djms    upperi         ; I
        djms    upperj         ; J
        djms    upperk         ; K
        djms    upperl         ; L
        djms    upperm         ; M
        djms    uppern         ; N
        djms    uppero         ; O
        djms    upperp         ; P
        djms    upperq         ; Q
        djms    upperr         ; R
        djms    uppers         ; S
        djms    uppert         ; T
        djms    upperu         ; U
        djms    upperv         ; V
        djms    upperw         ; W
        djms    upperx         ; X
        djms    uppery         ; Y
        djms    upperz         ; Z
        djms    lsquare        ; [
        djms    slosh          ; \
        djms    rsquare        ; ]
        djms    hat            ; ^
        djms    unders         ; _
        djms    bquote         ; `
        drjm                   ; 
dlist3  djms    lowera         ; a
        djms    lowerb         ; b
        djms    lowerc         ; c
        djms    lowerd         ; d
        djms    lowere         ; e
        djms    lowerf         ; f
        djms    lowerg         ; g
        djms    lowerh         ; h
        djms    loweri         ; i
        djms    lowerj         ; j
        djms    lowerk         ; k
        djms    lowerl         ; l
        djms    lowerm         ; m
        djms    lowern         ; n
        djms    lowero         ; o
        djms    lowerp         ; p
        djms    lowerq         ; q
        djms    lowerr         ; r
        djms    lowers         ; s
        djms    lowert         ; t
        djms    loweru         ; u
        djms    lowerv         ; v
        djms    lowerw         ; w
        djms    lowerx         ; x
        djms    lowery         ; y
        djms    lowerz         ; z
        djms    lcurl          ; {
        djms    pipe           ; |
        djms    rcurl          ; }
        djms    tilde          ; ~
        djms    del            ; DEL
        djms    cursn          ;
        djms    curso          ;
        djms    nl             ;
        drjm                   ; 
dlist4  djms    uppert         ;
        djms    lowerh         ;
        djms    lowere         ;
        djms    space          ;
        djms    lowerq         ;
        djms    loweru         ;
        djms    loweri         ;
        djms    lowerc         ;
        djms    lowerk         ;
        djms    space          ;
        djms    lowerb         ;
        djms    lowerr         ;
        djms    lowero         ;
        djms    lowerw         ;
        djms    lowern         ;
        djms    space          ;
        djms    lowerf         ;
        djms    lowero         ;
        djms    lowerx         ;
        djms    space          ;
        djms    lowerj         ;
        djms    loweru         ;
        djms    lowerm         ;
        djms    lowerp         ;
        djms    lowers         ;
        djms    space          ;
        djms    lowero         ;
        djms    lowerv         ;
        djms    lowere         ;
        djms    lowerr         ;
        djms    space          ;
        djms    lowert         ;
        djms    lowerh         ;
        djms    lowere         ;
        djms    space          ;
        djms    lowerl         ;
        djms    lowera         ;
        djms    lowerz         ;
        djms    lowery         ;
        djms    space          ;
        djms    lowerd         ;
        djms    lowero         ;
        djms    lowerg         ;
        djms    dot            ;
        drjm                   ;
;-------------------------------
; Short vector characters
;-------------------------------
space   inc    e,f             ; space
exclam  inc    e,d30           ; !
        inc    b00,d02         ; 
        inc    b03,02          ; 
        inc    b02,f           ; 
dquote  inc    e,d23           ; "
        inc    03,b0-1         ; 
        inc    -10,01          ; 
        inc    13,d30          ; 
        inc    b-1-3,0-1       ; 
        inc    10,01           ; 
        inc    f,f             ; 
hash    inc    e,b13           ; #
        inc    13,13           ; 
        inc    d30,b-1-3       ; 
        inc    -1-3,-1-3       ; 
        inc    d23,b-30        ; 
        inc    -30,d13         ; 
        inc    b30,30          ; 
        inc    f,f             ; 
dollar  inc    e,d3-2          ; $
        inc    b03,03          ; 
        inc    03,03           ; 
        inc    d3-2,b-30       ; 
        inc    -3-2,3-2        ; 
        inc    3-2,-3-2        ; 
        inc    -30,f           ; 
percent inc    e,d20           ; %
        inc    b13,21          ; 
        inc    1-2,-2-1        ; 
        inc    -12,02          ; 
        inc    -12,-2-1        ; 
        inc    1-2,21          ; 
        inc    12,12           ; 
        inc    f,f             ; 
amp     inc    e,d30           ; &
        inc    30,b-33         ; 
        inc    -23,12          ; 
        inc    10,1-2          ; 
        inc    -2-2,-2-1       ; 
        inc    0-2,2-1         ; 
        inc    20,23           ; 
        inc    f,f             ; 
quote   inc    e,d23           ; '
        inc    03,b0-1         ; 
        inc    10,01           ; 
        inc    -13,f           ; 
lparen  inc    e,d30           ; (
        inc    b-11,-12        ; 
        inc    02,12           ; 
        inc    11,f            ; 
rparen  inc    e,d20           ; )
        inc    b11,12          ; 
        inc    02,-12          ; 
        inc    -11,f           ; 
star    inc    e,d03           ; *
        inc    b32,32          ; 
        inc    d-31,b0-3       ; 
        inc    0-3,d31         ; 
        inc    b-32,-32        ; 
        inc    f,f             ; 
plus    inc    e,d31           ; +
        inc    b03,03          ; 
        inc    d-3-3,b30       ; 
        inc    30,f            ; 
comma   inc    e,d2-2          ; ,
        inc    b13,01          ; 
        inc    -10,0-1         ; 
        inc    f,f             ; 
minus   inc    e,d13           ; -
        inc    b30,30          ; 
        inc    f,f             ; 
dot     inc    e,d30           ; .
        inc    b00,f           ; 
slash   inc    e,d20           ; /
        inc    b13,13          ; 
        inc    13,f            ; 
zero    inc    e,d12           ; 0
        inc    b02,02          ; 
        inc    22,2-2          ; 
        inc    0-2,0-2         ; 
        inc    -2-2,-22        ; 
        inc    f,f             ; 
one     inc    e,d10           ; 1
        inc    b20,20          ; 
        inc    d-20,b03        ; 
        inc    03,02           ; 
        inc    -2-2,f          ; 
two     inc    e,d03           ; 2
        inc    03,b22          ; 
        inc    20,2-2          ; 
        inc    -1-2,-2-1       ; 
        inc    -3-3,30         ; 
        inc    30,f            ; 
three   inc    e,b30           ; 3
        inc    32,-22          ; 
        inc    -30,d30         ; 
        inc    b22,-22         ; 
        inc    -30,f           ; 
four    inc    e,d30           ; 4
        inc    10,b03          ; 
        inc    03,02           ; 
        inc    -3-3,-1-2       ; 
        inc    30,30           ; 
        inc    f,f             ; 
five    inc    e,b30           ; 5
        inc    31,02           ; 
        inc    -32,-30         ; 
        inc    03,30           ; 
        inc    30,f            ; 
six     inc    e,d03           ; 6
        inc    b21,20          ; 
        inc    2-2,-2-2        ; 
        inc    -20,-22         ; 
        inc    03,23           ; 
        inc    20,2-2          ; 
        inc    f,f             ; 
seven   inc    e,b23           ; 7
        inc    33,12           ; 
        inc    -30,-30         ; 
        inc    f,f             ; 
eight   inc    e,d20           ; 8
        inc    b20,21          ; 
        inc    02,-31          ; 
        inc    -32,22          ; 
        inc    20,2-2          ; 
        inc    -3-2,-3-1       ; 
        inc    0-2,2-1         ; 
        inc    f,f             ; 
nine    inc    e,d2-1          ; 9
        inc    b23,13          ; 
        inc    03,-30          ; 
        inc    -2-2,2-2        ; 
        inc    20,f            ; 
colon   inc    e,d32           ; :
        inc    b00,d03         ; 
        inc    01,b00          ; 
        inc    f,f             ; 
semcol  inc    e,d2-2          ; ;
        inc    b13,01          ; 
        inc    -10,10          ; 
        inc    d03,01          ; 
        inc    b-10,f          ; 
lt      inc    e,d31           ; <
        inc    30,b-21         ; 
        inc    -21,-21         ; 
        inc    21,21           ; 
        inc    21,f            ; 
equal   inc    e,d13           ; =
        inc    b30,30          ; 
        inc    d02,b-30        ; 
        inc    -30,f           ; 
gt      inc    e,d01           ; >
        inc    b21,21          ; 
        inc    21,-21          ; 
        inc    -21,-21         ; 
        inc    f,f             ; 
query   inc    e,d30           ; ?
        inc    b00,d02         ; 
        inc    b02,22          ; 
        inc    -12,-20         ; 
        inc    -1-2,f          ; 
at      inc    e,d30           ; @
        inc    b-31,02         ; 
        inc    02,22           ; 
        inc    30,1-3          ; 
        inc    -1-2,-30        ; 
        inc    02,20           ; 
        inc    0-2,f           ; 
uppera  inc    e,b13           ; A
        inc    13,12           ; 
        inc    1-3,1-3         ; 
        inc    1-2,d-23        ; 
        inc    b-30,f          ; 
upperb  inc    e,b03           ; b
        inc    03,02           ; 
        inc    30,2-1          ; 
        inc    0-2,-2-1        ; 
        inc    -30,d30         ; 
        inc    b3-1,0-2        ; 
        inc    -3-1,-30        ; 
        inc    f,f             ; 
upperc  inc    e,d32           ; C
        inc    30,b-2-2        ; 
        inc    -20,-22         ; 
        inc    03,23           ; 
        inc    20,2-2          ; 
        inc    f,f             ; 
upperd  inc    e,b03           ; d
        inc    03,02           ; 
        inc    30,2-1          ; 
        inc    1-2,0-2         ; 
        inc    -1-2,-2-1       ; 
        inc    -30,f           ; 
uppere  inc    e,b03           ; E
        inc    03,02           ; 
        inc    30,30           ; 
        inc    d-1-2,-1-2      ; 
        inc    b-20,-20        ; 
        inc    d0-2,0-2        ; 
        inc    b30,30          ; 
        inc    f,f             ; 
upperf  inc    e,b03           ; F
        inc    02,30           ; 
        inc    d-30,b03        ; 
        inc    30,30           ; 
        inc    f,f             ; 
upperg  inc    e,d33           ; G
        inc    b30,-1-3        ; 
        inc    -30,-23         ; 
        inc    03,32           ; 
        inc    3-1,f           ; 
upperh  inc    e,b03           ; H
        inc    03,02           ; 
        inc    d0-3,0-1        ; 
        inc    b30,30          ; 
        inc    y,b03           ; 
        inc    03,02           ; 
        inc    y,f             ; 
upperi  inc    e,b30           ; I
        inc    30,d-31         ; 
        inc    b03,03          ; 
        inc    d-31,b30        ; 
        inc    30,f            ; 
upperj  inc    e,d02           ; J
        inc    b2-2,20         ; 
        inc    22,03           ; 
        inc    03,f            ; 
upperk  inc    e,b03           ; K
        inc    03,02           ; 
        inc    d0-3,0-1        ; 
        inc    b32,32          ; 
        inc    y,b-13          ; 
        inc    -23,f           ; 
upperl  inc    e,b03           ; L
        inc    03,02           ; 
        inc    y,b30           ; 
        inc    30,f            ; 
upperm  inc    e,b03           ; M
        inc    03,02           ; 
        inc    3-3,33          ; 
        inc    0-3,0-3         ; 
        inc    0-2,f           ; 
uppern  inc    e,b03           ; N
        inc    03,02           ; 
        inc    2-3,2-3         ; 
        inc    2-2,03          ; 
        inc    03,02           ; 
        inc    f,f             ; 
uppero  inc    e,d10           ; O
        inc    b20,20          ; 
        inc    13,02           ; 
        inc    -13,-20         ; 
        inc    -20,-1-3        ; 
        inc    0-2,1-3         ; 
        inc    f,f             ; 
upperp  inc    e,b03           ; P
        inc    03,02           ; 
        inc    30,3-1          ; 
        inc    0-2,-3-1        ; 
        inc    -30,f           ; 
upperq  inc    e,d10           ; Q
        inc    b30,23          ; 
        inc    03,-12          ; 
        inc    -30,-2-3        ; 
        inc    0-3,1-2         ; 
        inc    d33,b3-3        ; 
        inc    f,f             ; 
upperr  inc    e,b03           ; R
        inc    03,02           ; 
        inc    30,3-1          ; 
        inc    0-2,-3-1        ; 
        inc    -30,d30         ; 
        inc    b2-2,1-2        ; 
        inc    f,f             ; 
uppers  inc    e,d01           ; S
        inc    b2-1,30         ; 
        inc    13,-31          ; 
        inc    -31,13          ; 
        inc    30,2-1          ; 
        inc    f,f             ; 
uppert  inc    e,d30           ; T
        inc    b03,03          ; 
        inc    02,x            ; 
        inc    b30,30          ; 
        inc    f,f             ; 
upperu  inc    e,d03           ; U
        inc    03,02           ; 
        inc    b0-3,0-3        ; 
        inc    2-2,20          ; 
        inc    22,03           ; 
        inc    03,f            ; 
upperv  inc    e,d03           ; V
        inc    03,02           ; 
        inc    b1-2,1-3        ; 
        inc    1-3,12          ; 
        inc    13,13           ; 
        inc    f,f             ; 
upperw  inc    e,b03           ; W
        inc    03,02           ; 
        inc    y,b33           ; 
        inc    3-3,03          ; 
        inc    03,02           ; 
        inc    f,f             ; 
upperx  inc    e,b23           ; X
        inc    22,23           ; 
        inc    y,b-23          ; 
        inc    -22,-23         ; 
        inc    f,f             ; 
uppery  inc    e,d30           ; Y
        inc    b02,03          ; 
        inc    33,x            ; 
        inc    b3-3,f          ; 
upperz  inc    e,d30           ; Z
        inc    30,b-30         ; 
        inc    -30,23          ; 
        inc    22,23           ; 
        inc    -30,-30         ; 
        inc    f,f             ; 
lsquare inc    e,d30           ; [
        inc    10,b-20         ; 
        inc    03,03           ; 
        inc    02,20           ; 
        inc    f,f             ; 
slosh   inc    e,d30           ; \
        inc    10,b-13         ; 
        inc    -13,-12         ; 
        inc    f,f             ; 
rsquare inc    e,d20           ; ]
        inc    b20,03          ; 
        inc    03,02           ; 
        inc    -20,f           ; 
hat     inc    e,d30           ; ^
        inc    b03,03          ; 
        inc    02,-1-2         ; 
        inc    -2-2,31         ; 
        inc    3-1,-22         ; 
        inc    -12,f           ; 
unders  inc    e,d-2-2         ; _
        inc    b30,30          ; 
        inc    20,20           ; 
        inc    d-23,f          ; 
bquote  inc    e,d13           ; `
        inc    03,b-22         ; 
        inc    f,f             ; 
lowera  inc    e,d03           ; a
        inc    03,b30          ; 
        inc    2-2,-1-3        ; 
        inc    2-1,d-21        ; 
        inc    b-3-1,-12       ; 
        inc    21,20           ; 
        inc    f,f             ; 
lowerb  inc    e,b03           ; b
        inc    03,03           ; 
        inc    y,d02           ; 
        inc    b3-2,21         ; 
        inc    03,-22          ; 
        inc    -3-2,f          ; 
lowerc  inc    e,d32           ; c
        inc    20,b-2-2        ; 
        inc    -20,-12         ; 
        inc    02,22           ; 
        inc    3-1,f           ; 
lowerd  inc    e,d33           ; d
        inc    21,b-32         ; 
        inc    -2-2,0-3        ; 
        inc    2-1,32          ; 
        inc    d0-2,b03        ; 
        inc    03,03           ; 
        inc    f,f             ; 
lowere  inc    e,d13           ; e
        inc    b20,20          ; 
        inc    -23,-20         ; 
        inc    -1-2,0-3        ; 
        inc    2-1,30          ; 
        inc    f,f             ; 
lowerf  inc    e,d20           ; f
        inc    b03,03          ; 
        inc    22,2-1          ; 
        inc    d-1-2,b-30      ; 
        inc    -20,f           ; 
lowerg  inc    e,d0-2          ; g
        inc    b3-1,22         ; 
        inc    02,03           ; 
        inc    -32,-2-2        ; 
        inc    0-3,2-1         ; 
        inc    32,f            ; 
lowerh  inc    e,b03           ; h
        inc    03,03           ; 
        inc    d1-3,b20        ; 
        inc    1-3,0-3         ; 
        inc    f,f             ; 
loweri  inc    e,d30           ; i
        inc    b03,03          ; 
        inc    d02,b00         ; 
        inc    f,f             ; 
lowerj  inc    e,b1-2          ; j
        inc    20,12           ; 
        inc    03,03           ; 
        inc    d02,b00         ; 
        inc    f,f             ; 
lowerk  inc    e,b03           ; k
        inc    03,03           ; 
        inc    d3-2,b-3-3      ; 
        inc    3-1,2-3         ; 
        inc    f,f             ; 
lowerl  inc    e,d30           ; l
        inc    b-11,03         ; 
        inc    02,02           ; 
        inc    f,f             ; 
lowerm  inc    e,b03           ; m
        inc    03,d0-2         ; 
        inc    b22,1-2         ; 
        inc    22,1-2          ; 
        inc    0-2,0-2         ; 
        inc    d-30,b03        ; 
        inc    f,f             ; 
lowern  inc    e,b03           ; n
        inc    03,d0-2         ; 
        inc    b32,2-3         ; 
        inc    0-3,f           ; 
lowero  inc    e,d10           ; o
        inc    b20,22          ; 
        inc    02,-12          ; 
        inc    -20,-2-2        ; 
        inc    0-2,1-2         ; 
        inc    f,f             ; 
lowerp  inc    e,d0-2          ; p
        inc    b03,03          ; 
        inc    03,d0-1         ; 
        inc    b30,1-2         ; 
        inc    -1-2,-30        ; 
        inc    f,f             ; 
lowerq  inc    e,d32           ; q
        inc    20,b-3-2        ; 
        inc    -21,03          ; 
        inc    22,3-2          ; 
        inc    0-3,0-2         ; 
        inc    0-2,a0173       ; 
lowerr  inc    e,b03           ; r
        inc    03,d0-3         ; 
        inc    b22,31          ; 
        inc    f,f             ; 
lowers  inc    e,d01           ; s
        inc    b3-1,22         ; 
        inc    -21,-31         ; 
        inc    22,3-1          ; 
        inc    f,f             ; 
lowert  inc    e,d30           ; t
        inc    b-11,03         ; 
        inc    02,02           ; 
        inc    d-2-2,b20       ; 
        inc    20,f            ; 
loweru  inc    e,d03           ; u
        inc    03,b0-2         ; 
        inc    0-2,1-2         ; 
        inc    20,22           ; 
        inc    02,02           ; 
        inc    y,d02           ; 
        inc    b1-2,f          ; 
lowerv  inc    e,d03           ; v
        inc    03,b2-3         ; 
        inc    1-3,13          ; 
        inc    13,f            ; 
lowerw  inc    e,d03           ; w
        inc    03,b1-3         ; 
        inc    1-3,13          ; 
        inc    1-3,1+3         ; 
        inc    13,f            ; 
lowerx  inc    e,b23           ; x
        inc    33,d-20         ; 
        inc    -30,b3-3        ; 
        inc    2-3,f           ; 
lowery  inc    e,d1-3          ; y
        inc    b23,23          ; 
        inc    03,x            ; 
        inc    b1-3,2-3        ; 
        inc    f,f             ; 
lowerz  inc    e,b30           ; z
        inc    20,a011         ; 
        inc    b23,33          ; 
        inc    -30,-20         ; 
        inc    f,f             ; 
lcurl   inc    e,d33           ; {
        inc    03,b-20         ;
        inc    1-3,-10         ;
        inc    d10,b-1-3       ;
        inc    20,f            ;
pipe    inc    e,d33           ; |
        inc    03,01           ;
        inc    b0-3,d0-2       ;
        inc    b0-3,a0173      ;
rcurl   inc    e,d13           ; }
        inc    03,b20          ;
        inc    -1-3,10         ;
        inc    d-10,b1-3       ;
        inc    -20,f           ;
tilde   inc    e,d03           ; ~
        inc    b12,1-2         ;
        inc    1-2,12          ;
        inc    f,f             ;
del     inc    e,b+0+3         ; DEL (filled box)
        inc    b+0+3,b+1+0     ;
        inc    b+0-3,b+0-3     ;
        inc    b+1+0,b+0+3     ;
        inc    b+0+3,b+1+0     ;
        inc    b+0-3,b+0-3     ;
        inc    b+1+0,b+0+3     ;
        inc    b+0+3,f         ;
cursn   inc    e,b03           ; cursor on
        inc    03,30           ; 
        inc    30,0-3          ; 
        inc    0-3,-30         ; 
        inc    -30,d11         ; 
        inc    b02,02          ; 
        inc    20,20           ; 
        inc    0-2,0-2         ; 
        inc    -30,03          ; 
        inc    20,0-2          ; 
        inc    -10,01          ; 
        inc    f,f             ; 
curso   inc    e,b03           ; cursor off
        inc    03,30           ; 
        inc    30,0-3          ; 
        inc    0-3,-30         ; 
        inc    -30,f           ; 
nlx     inc    e,d12           ; newline
        inc    b03,3-3         ; 
        inc    03,d2-2         ; 
        inc    b0-3,30         ; 
        inc    f,f             ; 
nl      inc    e,d12           ; newline
        inc    b03,2-3         ; 
        inc    03,d0-3         ; 
        inc    b0-1,20         ; 
        inc    d1-1,b03        ; 
        inc    03,-30          ; 
        inc    -30,0-3         ; 
        inc    0-3,30          ; 
        inc    30,f            ; 
nl2     inc    e,d33           ; newline
        inc    b0-2,-1-2       ; 
        inc    -2-2,02         ;
        inc    d0-2,b20        ; 
        inc    f,f             ; 
;-------------------------------
        end
