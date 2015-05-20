             /* ; Imlac Papertape Program Block Loader                                          */
             /* ;                                                                               */
             /* ; This loader is loaded by the bootstrap program at x7700, where x=0 for        */
             /* ; a 4K machine, and x=1 for an 8K machine.                                      */
             /* ;                                                                               */
             /* ; The load format consists of one or more contiguous blocks, with no            */
             /* ; padding bytes between them.  Each block begins with three words:              */
             /* ;                                                                               */
             /* ;          load address                                                         */
             /* ;          negative word count                                                  */
             /* ;          checksum                                                             */
             /* ;                                                                               */
             /* ; Words are always received high-order byte first.  The rest of the block       */
             /* ; consists of "word count" words, which are loaded starting at "load address".  */
             /* ; The sum of all the words in the block, including these first three, must be   */
             /* ; zero (16 bit sum), and the checksum is computed to give that result.          */
             /* ;                                                                               */
             /* ; The end of the load is signalled by a block with a negative starting address. */
             /* ; If that address is -1, the loader simply halts.  Otherwise it reads one more  */
             /* ; word (in the position normally occupied by the negative word count), which    */
             /* ; will be the value in the AC at the start of the program just loaded.  Then    */
             /* ; it starts the program with an indirect jump through the negative starting     */
             /* ; address.  (For example, to start at 00100, the starting address will be       */
             /* ; 100100).                                                                      */
             /* ;                                                                               */
             /* ; If a checksum error occurs, the loader goes into a tight loop at CSERR.       */
             /* ;                                                                               */
             /* ;    As decoded by Howard Palmer (hep@acm.org) from an Imlac wumpus binary.     */
             /* ;    Oct. 6, 2004                                                               */
             /* ;    Modified by Ross Wilson (wilsonr@iinet.net.au) to load papertape.          */
             /* ;                                                                               */
             /*               ORG 37700               ;                                         */
    0100011, /* 037700 BLOCK: CAL                     ; Initialize checksum to zero             */
    0023731, /* 037701        DAC   CKSM              ;                                         */
    0037732, /* 037702        JMS   RWORD             ; Read the load address of the next block */
    0023727, /* 037703        DAC   START             ; Save it                                 */
    0002002, /* 037704        ASP                     ; Looking for a negative load address     */
    0013722, /* 037705        JMP   DONE              ; Finished loading blocks if we find it   */
    0037732, /* 037706        JMS   RWORD             ; Read the negative word count            */
    0023730, /* 037707        DAC   CNT               ;                                         */
    0037732, /* 037710        JMS   RWORD             ; Read the checksum word                  */
    0037732, /* 037711 LOAD:  JMS   RWORD             ; Read next word to be loaded             */
    0123727, /* 037712        DAC  @START             ; Store it                                */
    0033727, /* 037713        ISZ   START             ; Bump the load address                   */
    0033730, /* 037714        ISZ   CNT               ; Bump the negative count                 */
    0013711, /* 037715        JMP   LOAD              ; Loop until it goes to zero              */
    0067731, /* 037716        ADD   CKSM              ; Finish computing the checksum           */
    0002001, /* 037717        ASZ                     ; Should add up to zero                   */
    0013720, /* 037720 CSERR: JMP   CSERR             ; Tight loop if checksum error            */
    0013700, /* 037721        JMP   BLOCK             ; Loop back for the next block            */
             /*                                       ;                                         */
    0100004, /* 037722 DONE:  IAC                     ; Increment the negative load address     */
    0102001, /* 037723        ASN                     ; Just stop if it goes to zero            */
    0000000, /* 037724        HLT                     ; Load completed successfully             */
    0037732, /* 037725        JMS   RWORD             ; If not zero, read a starting value for the AC */
    0113727, /* 037726        JMP  @START             ; And use the negative load address to start */
             /*                                       ;                                         */
    0000000, /* 037727 START: WORD  0                 ; block start address                     */
    0000000, /* 037730 CNT:   WORD  0                 ; block word count                        */
    0000000, /* 037731 CKSM:  WORD  0                 ; block checksum                          */
             /*                                                                                 */
             /*        ; This subroutine reads the next word.  It is entered with either zero or the */
             /*        ; last word read in the AC.  It adds that value to CKSM.                 */
             /*                                                                                 */
    0000000, /* 037732 RWORD: WORD  0                 ; Subroutine to read a word               */
    0067731, /* 037733        ADD   CKSM              ; Accumulate checksum                     */
    0023731, /* 037734        DAC   CKSM              ;                                         */
    0100011, /* 037735        CAL                     ;                                         */
    0102400, /* 037736 WT1:   HSN                     ; Wait for high-order byte                */
    0013736, /* 037737        JMP   WT1               ;                                         */
    0002400, /* 037740 WT2:   HSF                     ;                                         */
    0013740, /* 037741        JMP   WT2               ;                                         */
    0001051, /* 037742        HRB                     ; Read it                                 */
    0003003, /* 037743        RAL   3                 ; Move it to the high-order AC            */
    0003003, /* 037744        RAL   3                 ;                                         */
    0003002, /* 037745        RAL   2                 ;                                         */
    0102400, /* 037746 WT3:   HSN                     ; Wait for low-order byte                 */
    0013746, /* 037747        JMP   WT3               ;                                         */
    0002400, /* 037750 WT4:   HSF                     ;                                         */
    0013750, /* 037751        JMP   WT4               ;                                         */
    0001051, /* 037752        HRB                     ; Read it, forming a word                 */
    0113732, /* 037753        JMP  @RWORD             ; Return to caller                        */
             /*                                                                                 */
    0000000, /* 037754        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037755        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037756        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037757        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037760        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037761        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037762        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037763        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037764        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037765        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037766        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037767        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037770        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037771        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037772        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037773        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037774        WORD 0                  ; Filler to 076 words                     */
    0000000, /* 037775        WORD 0                  ; Filler to 076 words                     */
    0000000  /* 037776        WORD 0                  ; Filler to 076 words                     */
             /*                                                                                 */
             /*               END                     ;                                         */
