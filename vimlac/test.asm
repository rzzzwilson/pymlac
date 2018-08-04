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
        dhvc                   ;
        dsts    0              ; 
        dlxa    020            ; 
        dlya    0100           ; 
        djms    upperf         ; F
        djms    upperg         ; G
        djms    upperh         ; H
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
;-------------------------------
        end
