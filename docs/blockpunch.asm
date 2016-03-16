; typed in from imlacdocs/blockpunchsrc.pdf
        org     037540
start   hlt             ; wait for first address
        lda             ;
        dac     fad     ; save in FAD
        hlt             ; wait for end address
        lda             ;
        sub     fad     ; get length of block punch
        cma             ; ones complement the count
        dac     mwd     ; save as 'minus number of words'
        asm             ; test if end address < first
        jmp     start   ; jump if so
doblk   add     allbits ; test if num words 
        asp             ; skip if
        cla             ;
        sub     allbits ;
        dac     wtb     ; save in 'words this block'
        cia             ; twos complement block count
        jms     pbyte   ; output word count BYTE
        add     mwd     ;
        dac     mwd     ;
        lac     fad     ;
        jms     pword   ; output block address WORD
        cla             ;
        dac     smc     ;
loop    lac     *fad    ;
        jms     pword   ;
        jms     updchs  ; update checksum
        isz     fad     ; move address to next word
        isz     wtb     ; check block finished
        jmp     loop    ; jump if NOT, continue
        lac     smc     ; 
        jms     pword   ; outp[ut checksum WORD
        lac     mwd     ; are we finished the block punch?
        asz             ; skip if no more words to punch
        jmp     doblk   ; punch next block
        jmp     start   ; punch finished
;------------------------
; Punch two bytes (a WORD) from AC
;------------------------
pword   bss     1       ;
        rar     3       ; shift high byte to lower in AC
        rar     3       ;
        rar     2       ;
        jms     pbyte   ; punch high byte
        ral     3       ; get low byte to AC low byte
        ral     3       ;
        ral     2       ;
        jms     pbyte   ; punch low byte
        jmp     *pword  ;
;------------------------
; Punch low byte of AC (AC left unchanged)
;------------------------
pbyte   bss     1       ;
        tsf             ; skip if TTYOUT free
        jmp     .-1     ; wait until TTYOUT is free
        tpc             ; punch and clear flag
        jmp     *pbyte  ;
;------------------------
; Update checksum, new value in AC
;------------------------
updchs  bss     1       ;
        cll             ; clear link
        add     smc     ; add new value
        lsz             ; skip if no overflow
        iac             ; else increment checksum
        dac     smc     ; put updated checksum back
        jmp     *updchs ;
;------------------------
; What were literals in original code stored here
;------------------------
fad     data    0       ; first address
mwd     data    0       ; minus number of words
wtb     data    0       ; num words in this block
smc     data    0       ; checksum
allbits data    0377    ; byte of all bits

;------------------------
; Punch block loader
;------------------------
        org     start+0100 ; 037540 + 0100 = 037640
pbldr   lwc     0100    ;
        dac     fad     ;
        lwc     076     ;
        dac     wtb     ;
pbloop  lac     *fad    ;
        jms     pword   ;
        isz     fad     ;
        isz     wtb     ;
        jmp     pbloop  ;
        jmp     pldr    ; punch leader

;------------------------
; Punch leader
;------------------------
        org     start+0120 ; 037540 + 0120 = 037660
pldr    lwc     07      ; we want 16 bytes of leader (8 words)
        dac     wtb     ; store leader count
        cla             ;
        jms     pword   ;
        isz     wtb     ;
        jmp     .-2     ;
        jmp     start   ; wait for first address

;------------------------
; Punch end code
;------------------------
        org     start+0130 ; 037540 + 0130 = 037670
pend    law     0377    ;
        jms     pbyte   ;
        jms     pbyte   ;
        jms     pbyte   ;
        jmp     pldr    ; punch more leader

        end
