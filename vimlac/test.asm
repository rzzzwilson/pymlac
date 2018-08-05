;-------------------------------
; Test of display processor instructions 
; Display characters on screen.
;-------------------------------
        org     0100           ; 
        dof                    ; 
loop    dsn                    ; wait until display is off
        jmp     loop           ; 
        law     dsub           ; start display
        dla                    ; 
        don                    ; 
        jmp     loop           ; keep going
;-------------------------------
; Display list subroutine - show ASCII chars 'ABC'
;-------------------------------
dsub 
        dsts    0              ; 
        dlxa    020            ; 
        dlya    0100           ; 
        djms    upperf         ; F
        djms    upperg         ; G
        djms    upperh         ; H
        djms    upperi         ; I
        djms    upperj         ; J
        dhlt                   ;
;-------------------------------
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
;-------------------------------
        end
