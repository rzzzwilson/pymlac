; Imlac Program Loader
;
; This loader is loaded by the bootstrap program at x7700, where x=0 for
; a 4K machine, and x=1 for an 8K machine.  The first byte of this loader
; is 002, which is used by the bootstrap as a signal to start loading.
; This loader checks whether it is running at address 017700 on an 8K machine,
; which is assumed to support long vectors, and enables a simple display
; during the load if so.
;
; The load format consists of one or more contiguous blocks, with no
; padding bytes between them.  Each block begins with three words:
;
;          load address
;          negative word count
;          checksum
;
; Words are always received high-order byte first.  The rest of the block
; consists of "word count" words, which are loaded starting at "load address".
; The sum of all the words in the block, including these first three, must be
; zero (16 bit sum), and the checksum is computed to give that result.
;
; The end of the load is signalled by a block with a negative starting address.
; If that address is -1, the loader simply halts.  Otherwise it reads one more
; word (in the position normally occupied by the negative word count), which
; will be the value in the AC at the start of the program just loaded.  Then
; it starts the program with an indirect jump through the negative starting
; address.  (For example, to start at 00100, the starting address will be
; 100100).
;
; If a checksum error occurs, the loader goes into a tight loop at
; CSERR (x7736).
;
;    As decoded by Howard Palmer (hep@acm.org) from an Imlac wumpus binary.
;    Oct. 6, 2004
;
       ORG 37700
START: RCF                     ; This is overwritten by the block start address
CNT:   JMS   CNT               ; This instruction overwrites itself!
CKSM:  LAC   CNT               ; This is overwritten by the checksum
       SAM   LD8K              ; Are we loaded at 017700?
       JMP   NODSP             ; Yes, skip display code
       LWC   12                ; Get address of display list (DLIST at 037766)
       DLA                     ; Start the display processor
       DON
NODSP: CAL                     ; Initialize checksum to zero
       DAC   CKSM
       JMS   RWORD             ; Read the load address of the next block
       DAC   START             ; Save it
       ASP                     ; Looking for a negative load address
       JMP   DONE              ; Finished loading blocks if we find it
       JMS   RWORD             ; Read the negative word count
       DAC   CNT
       JMS   RWORD             ; Read the checksum word
LOAD:  JMS   RWORD             ; Read next word to be loaded
       DAC  @START             ; Store it
       LAC   START             ; Get the current load address
       SAR   3                 ; Extract the top 10 bits
       AND   M1777
       IOR   DLYA              ; Use as the Y value in a DLYA instruction
       DAC   DLIST             ; Replace the DLYA in the display list
       LAC  @START             ; Get the word that was just loaded
       ISZ   START             ; Bump the load address
       ISZ   CNT               ; Bump the negative count
       JMP   LOAD              ; Loop until it goes to zero
       ADD   CKSM              ; Finish computing the checksum
       ASZ                     ; Should add up to zero
CSERR: JMP   CSERR             ; Tight loop if checksum error
       JMP   NODSP             ; Loop back for the next block

DONE:  DOF                     ; Turn off the display processor
       IAC                     ; Increment the negative load address
       ASN                     ; Just stop if it goes to zero
       HLT                     ; Load completed successfully
       JMS   RWORD             ; If not zero, read a starting value for the AC
       JMP  @START             ; And use the negative load address to start

; This subroutine reads the next word.  It is entered with either zero or the
; last word read in the AC.  It adds that value to CKSM.

RWORD: ZZZ                     ; Subroutine to read a word
       ADD   CKSM              ; Accumulate checksum
       DAC   CKSM
       CAL
WT1:   RSF                     ; Wait for high-order byte
       JMP   WT1
       RRC                     ; Read it
       RAL   3                 ; Move it to the high-order AC
       RAL   3
       RAL   2
WT2:   RSF                     ; Wait for low-order byte
       JMP   WT2
       RRC                     ; Read it, forming a word
       JMP  @RWORD             ; Return to caller
DLYA:  DLYA  0                 ; Used to build DLYA instruction
M1777: DATA  1777              ; 10-bit mask

; Begin display list
;    This must start at location 037766

DLIST: DLYA  0                 ; This gets dynamically updated
       DLXA  0
       DSTS  1                 ; Set normal scale
       DATA  046000            ; 3-word long vector
       DATA  021777            ; x=1777, y=0, beam on
       DATA  0
       DJMP  DLIST             ; Run the display processor continuously
LD8K:  DATA  017702            ; Used to check for load at 017700
       END
