SECTION code_user
PUBLIC _main

EXTERN PCMPLAY

_main:
; ====================================================================================================
; PSGPCMPlayer Test Program
; ====================================================================================================

    LD HL,PCMDATA
    LD DE,PCMDATA_END - PCMDATA
    CALL PCMPLAY

.LOOP
    JP LOOP

; ====================================================================================================
; 定数エリア
; romに格納される
; ====================================================================================================
SECTION rodata_user

PCMDATA:
    INCBIN "assets/sample_8.pcm"
PCMDATA_END:
    DB $7F
