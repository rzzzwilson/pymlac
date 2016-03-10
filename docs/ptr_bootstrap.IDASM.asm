; PTR bootstrap code, as disassembled by 'idasm'
; with hand touch-ups
	ORG	00040	; addr  code

	LAC	bladdr	; 00040 0060077 ; loc 010 holds block loader address
	DAC	010	; 00041 0020010
	LWC	076	; 00042 0104076 ; loc 010 holds block loadr word count
	DAC	020	; 00043 0020020
	HON		; 00044 0001061 ; turn PTR on
skipz	CAL		; 00045 0100011 ; wait until zero leader is finished
	HSF		; 00046 0002400
	JMP	.-1	; 00047 0010046
	HRB		; 00050 0001051
	SAM	stbyte	; 00051 0074075 ; that is, wait until 02 byte
	JMP	skipz	; 00052 0010045
rdloop	HSF		; 00053 0002400 ; read next byte
	JMP	.-1	; 00054 0010053 ; (note we re-read the initial 02 byte)
	HRB		; 00055 0001051
	RAL	3	; 00056 0003003 ; shift 8 bits left
	RAL	3	; 00057 0003003
	RAL	2	; 00060 0003002
	HSN		; 00061 0102400
	JMP	.-1	; 00062 0010061
	HSF		; 00063 0002400 ; read next byte
	JMP	.-1	; 00064 0010063
	HRB		; 00065 0001051
	DAC	*010	; 00066 0120010 ; store into block loader space
	HSN		; 00067 0102400
	JMP	.-1	; 00070 0010067
	CAL		; 00071 0100011 ; zero AC ready for possible blockloader
	ISZ	020	; 00072 0030020 ; are we finished yet?
	JMP	rdloop	; 00073 0010053 ;     jump if not, get next word
	JMP	*blkldr	; 00074 0110076 ; yes, jump to the blockloader code

stbyte	DATA	000002	; 00075 0000002 ; the expected start byte
blkldr	DATA	037700	; 00076 0037700 ; base address of blockloader code
bladdr	DATA	037677	; 00077 0037677 ; ISZ pointer to store blockloader words

	END		;
