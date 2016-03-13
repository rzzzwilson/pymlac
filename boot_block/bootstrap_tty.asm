;------------------------
; TTY bootstrap code from images/imlacdocs/loading.pdf
;------------------------
                        ;
bladdr  equ     037700  ; address of top mem minus 0100
blsize  equ     0100    ; size of blockloader code
                        ;
	ORG	040	;
                        ;
	LAC	staddr	;
	DAC	010	; 010 points to loading word
	LWC	blsize-2;
	DAC	020	; 020 is ISZ counter of loader size
; skip all bytes until the expected byte
skpzer	RCF		; 
	CAL		;
	RSF		; wait for next byte
	JMP	.-1	;
	RRB		; get next TTY byte
	SAM	fbyte	; wait until it's the expected byte
	JMP	skpzer	;
nxtwrd	RSF		; wait until TTY byte ready
	JMP	.-1	;
	RRC		; get high byte and clear flag
	RAL	3	; shift into AC high byte
	RAL	3	;
	RAL	2	;
	RSF		; wait until next TTY byte
	JMP	.-1	;
	RRC		; get low byte and clear flag
	DAC	*010	; store word
	CAL		; clear AC ready for next word
	ISZ	020	; finished?
	JMP	nxtwrd	; jump if not
	JMP	*blstrt	; else execute the blockloader
                        ;
	DATA	000000	; empty space?
	DATA	000000	;
	DATA	000000	;
	DATA	000000	;
                        ;
fbyte	DATA	000002	; expected first byte of block loader
blstrt	data	bladdr	; start of blockloader code
staddr	data	bladdr-1; ISZ counter for blockloader size
                        ;
	END		;
