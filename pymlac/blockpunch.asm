; typed in from imlacdocs/blockpunchsrc.pdf
        org     037540
s       hlt             ; wait for first address
        lda             ;
        dac     fad     ; save in FAD
        hlt             ; wait for end address
        lda             ;
        sub     fad     ; get length of block punch
        cma             ; ones complement the count
        dac     mwd     ; save as 'minus number of words'
        asm             ; test if end address < first
        jmp     s       ; jump if so
e3      add     allbits ; test if num words 
        asp             ; skip if
        cla             ;
        sub     allbits ;
        dac     wtb     ; save in 'words this block'
        cia             ; twos complement block count
        jms     t       ; output word count BYTE
        add     mwd     ;
        dac     mwd     ;
        lac     fad     ;
        jms     t2      ; output block address WORD
        cla             ;
        dac     smc     ;
loop    lac     *fad    ;
        jms     t2      ;
        jms     s1      ; update checksum
        isz     fad     ; move address to next word
        isz     wtb     ; check block finished
        jmp     loop    ; jump if NOT, continue
        lac     smc     ; 
        jms     t2      ; outp[ut checksum WORD
        lac     mwd     ; are we finished the block punch?
        asz             ; skip if no more words to punch
        jmp     e3      ; punch next block
        jmp     s       ; punch finished
;------------------------
; Punch two bytes (a WORD) from AC
;------------------------
t2      bss     1       ;
        rar     3       ; shift high byte to lower in AC
        rar     3       ;
        rar     2       ;
        jms     t       ; punch high byte
        ral     3       ; get low byte to AC low byte
        ral     3       ;
        ral     2       ;
        jms     t       ; punch low byte
        jmp     *t2     ;
;------------------------
; Punch low byte of AC (AC left unchanged)
;------------------------
t       bss     1       ;
        tsf             ; skip if TTYOUT free
        jmp     .-1     ; wait until TTYOUT is free
        tpc             ; punch and clear flag
        jmp     *t      ;
;------------------------
; Update checksum, new value in AC
;------------------------
s1      bss     1       ;
        cll             ; clear link
        add     smc     ; add new value
        lsz             ; skip if no overflow
        iac             ; else increment checksum
        dac     smc     ; put updated checksum back
        jmp     *s1     ;
;------------------------
; What were literals in original code stored here
;------------------------
fad     data    0       ; first address
mwd     data    0       ; minus number of words
wtb     data    0       ; num words in this block
smc     data    0       ; checksum
allbits data    0377    ; byte of all bits

        org     s+0100  ; 037540 + 0100 = 037640
;------------------------
; Punch block loader
;------------------------
        lwc     0100    ;
        dac     fad     ;
        lwc     076     ;
        dac     wtb     ;
        lac     *fad    ;
        jms     t2      ;
        isz     fad     ;
        isz     wtb     ;
        jmp     .-4     ;
        jmp     s+0120  ; punch leader

        org     s+0120  ; 037540 + 0120 = 037660
;------------------------
; Punch leader
;------------------------
        lwc     012     ;
        dac     wtb     ; store leader count
        cla             ;
        jms     t2      ;
        isz     wtb     ;
        jmp     .-2     ;
        jmp     s       ; wait for first address

        org     s+0130  ; 037540 + 0130 = 037670
;------------------------
; Punch end code
;------------------------
        law     0377    ;
        jms     t       ;
        jms     t       ;
        jms     t       ;
        jmp     s+0120  ; punch more leader

        end
