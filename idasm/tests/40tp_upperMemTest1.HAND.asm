			;
	ORG	10010	; addr  code
L00010			; 10010 0000000
			;
	ORG	10100	; addr  code
	LAW	00001	; 10100 0004001
	DAC	L00143	; 10101 0020143
L00102	LAC	L00143	; 10102 0060143
	RAL	1	; 10103 0003001
	DAC	L00143	; 10104 0020143
	LWC	00001	; 10105 0104001
	DAC	L00010	; 10106 0020010
L00107	LAC	L00143	; 10107 0060143
	DAC	*L00010	; 10110 0120010
	CMA		; 10111 0100002
	DAC	*L00010	; 10112 0120010
	LAC	L00153	; 10113 0060153
	SAM	L00010	; 10114 0074010
	JMP	L00107	; 10115 0010107
	LWC	00001	; 10116 0104001
	DAC	L00010	; 10117 0020010
L00120	LAC	L00143	; 10120 0060143
	SAM	*L00010	; 10121 0174010
	JMS	L00132	; 10122 0034132
	CMA		; 10123 0100002
	SAM	*L00010	; 10124 0174010
	JMS	L00132	; 10125 0034132
	LAC	L00153	; 10126 0060153
	SAM	L00010	; 10127 0074010
	JMP	L00120	; 10130 0010120
	JMP	L00102	; 10131 0010102
L00132	HLT		; 10132 0000000
	DAC	L00144	; 10133 0020144
	LAC	L00010	; 10134 0060010
	HLT		; 10135 0000000
	DAC	L00145	; 10136 0020145
	LAC	*L00145	; 10137 0160145
	HLT		; 10140 0000000
	LAC	L00144	; 10141 0060144
	JMP	*L00132	; 10142 0110132
L00143	DATA	010163	; 10143 0010163
L00144	DATA	000000	; 10144 0000000
L00145	DATA	000000	; 10145 0000000
			;
	ORG	10153	; addr  code
L00153	DATA	007771	; 10153 0007771
	DATA	007776	; 10154 0007776
	DATA	010000	; 10155 0010000
	DATA	010006	; 10156 0010006
			;
	ORG	10163	; addr  code
	DATA	104001	; 10163 0104001
	DATA	124154	; 10164 0124154
	DATA	020146	; 10165 0020146
	DATA	060154	; 10166 0060154
	DATA	020147	; 10167 0020147
	DATA	020150	; 10170 0020150
	DATA	060147	; 10171 0060147
	DATA	064155	; 10172 0064155
	DATA	020147	; 10173 0020147
	DATA	100001	; 10174 0100001
	DATA	124147	; 10175 0124147
	DATA	020151	; 10176 0020151
	DATA	160150	; 10177 0160150
	DATA	102002	; 10200 0102002
	DATA	010205	; 10201 0010205
	DATA	060151	; 10202 0060151
	DATA	120147	; 10203 0120147
	DATA	010171	; 10204 0010171
	DATA	060146	; 10205 0060146
	DATA	120154	; 10206 0120154
	DATA	060147	; 10207 0060147
	DATA	070156	; 10210 0070156
	DATA	020152	; 10211 0020152
	DATA	010100	; 10212 0010100
			;
	ORG	37400	; addr  code
	DATA	001052	; 37400 0001052
	DATA	113402	; 37401 0113402
	DATA	010163	; 37402 0010163
			;
	ORG	37714	; addr  code
	DATA	013400	; 37714 0013400
	END		;
