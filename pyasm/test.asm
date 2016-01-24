; a test comment on the first line
        org     0100

start   law     10          ; comment
        lac     start2      ; another comment
        hlt

        org     0200 + 1
start2  
        lac     0100
        hlt

        end     start
