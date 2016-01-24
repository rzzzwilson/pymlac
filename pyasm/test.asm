; a test comment
        org     0000100

start   law     10          ; comment
        lac     start2      ; another comment
        hlt

        org     0200 + 1
start2  
        lac     0100
        hlt

        end     start
