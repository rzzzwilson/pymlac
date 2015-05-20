;;;;;;;;;;;;;;;;;;;;;;;;;
; check the shift and rotate instructions
;;;;;;;;;;;;;;;;;;;;;;;;;
	org	00100
; first, SAL instruction
	stl		; L <-1
	lwc	1	; AC <- 0177777
	sal	1	; AC <- 0177776, L unchanged
	sam	sal11	;
	hlt		;
	lsn		; link should still be 1
	hlt		; error, was 0
	cll		; L <- 0
	lwc	1	; AC <- 0177777
	sal	2	; AC <- 0177774, L unchanged
	sam	sal12	;
	hlt		;
	lsz		; link should still be 0
	hlt		; error, was 1
	lwc	1	;
	sal	3	; AC <- 0177770
	sam	sal13	;
	hlt		;
	lac	sal21b	; AC <- 0100001
	sal	1	; AC <- 0100002
	sam	sal21	;
	hlt		;
	lac	sal21b	; AC <- 0100001
	sal	2	; AC <- 0100004
	sam	sal22	;
	hlt		;
	lac	sal21b	; AC <- 0100001
	sal	3	; AC <- 0100010
	sam	sal23	;
	hlt		;
	lsz		; link should still be 0
	hlt		; error, was 1
; now test SAR
	stl		; L <- 1
	lwc	1	; AC <- 0177777
	sar	1	; AC <- 0177777
	sam	sar11	;
	hlt		;
	lsn		; L should still be 1
	hlt		;
	cll		; L <- 0
	lwc	1	;
	sar	2	; AC <- 0177777
	sam	sar12	;
	hlt		;
	lsz		; L should still be 0
	hlt		;
	lwc	1	;
	sar	3	; AC <- 0177777
	sam	sar13	;
	hlt		;
	lac	sar21b	; AC <- 0077777
	sar	1	; AC <- 0037777
	sam	sar21	;
	hlt		;
	lac	sar21b	;
	sar	2	; AC <- 0017777
	sam	sar22	;
	hlt		;
	lac	sar21b	;
	sar	3	; AC <- 0007777
	sam	sar23	;
	hlt		;
; test the RAR instruction
	cll		; L <- 0
	lac	rar11b	; AC <- 0100000
	rar	1	; AC <- 0040000
	sam	rar11	;
	hlt		;
	lsz		; L should be 0
	hlt		;
	cll		; L <- 0
	lac	rar11b	; AC <- 0100000
	rar	2	; AC <- 0020000
	sam	rar12	;
	hlt		;
	lsz		; L should be 0
	hlt		;
	cll		; L <- 0
	lac	rar11b	; AC <- 0100000
	rar	3	; AC <- 0010000
	sam	rar13	;
	hlt		;
	lsz		; L should be 0
	hlt		;
	stl		; L <- 1
	lac	rar11b	; AC <- 0100000
	rar	1	; AC <- 0140000
	sam	rar21	;
	hlt		;
	lsz		; L should be 0
	hlt		;
	stl		; L <- 1
	lac	rar11b	; AC <- 0100000
	rar	2	; AC <- 0060000
	sam	rar22	;
	hlt		;
	lsz		; L should be 0
	hlt		;
	stl		; L <- 1
	lac	rar11b	; AC <- 0100000
	rar	3	; AC <- 0030000
	sam	rar23	;
	hlt		;
	lsz		; L should be 0
	hlt		;
	cll		; L <- 0
	law	3	; AC <- 0000003
	rar	1	; L <- 1 AC <- 0000001
	sam	rar24	;
	hlt		;
	lsn		; L should be 1
	hlt		;
	stl		; L <- 1
	law	3	; AC <- 0000003
	rar	1	; L <- 1 AC <- 0100001
	sam	rar25	;
	hlt		;
	lsn		; L should be 1
	hlt		;
; test the RAL instruction
	cll		; L <- 0
	lac	ral11b	; AC <- 0100001
	ral	1	; L <- 1 AC <- 0000002
	sam	ral11	;
	hlt		;
	lsn		; L should be 1
	hlt		;
	stl		; L <- 1
	lac	ral11b	; AC <- 0100001
	ral	1	; L <- 1 AC <- 0000003
	sam	ral12	;
	hlt		;
	lsn		; L should be 1
	hlt		;
	stl		; L <- 1
	lac	ral11c	; AC <- 0000001
	ral	1	; L <- 0 AC <- 0000003
	sam	ral12	;
	hlt		;
	lsz		; L should be 0
	hlt		;
	hlt		;
; data for tests
zero	data	0	;
one	data	1	;
sal11	data	0177776	;
sal12	data	0177774	;
sal13	data	0177770	;
sal21b	data	0100001	;
sal21	data	0100002	;
sal22	data	0100004	;
sal23	data	0100010	;
sar11	data	0177777	;
sar12	data	0177777	;
sar13	data	0177777	;
sar21b	data	0077777	;
sar21	data	0037777	;
sar22	data	0017777	;
sar23	data	0007777	;
rar11b	data	0100000	;
rar11	data	0040000	;
rar12	data	0020000	;
rar13	data	0010000	;
rar21	data	0140000	;
rar22	data	0060000	;
rar23	data	0030000	;
rar24	data	0000001	;
rar25	data	0100001	;
ral11b	data	0100001	;
ral11c	data	0000001	;
ral11	data	0000002	;
ral12	data	0000003	;
	end
