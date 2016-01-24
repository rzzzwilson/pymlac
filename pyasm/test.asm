; a test comment on the first line
        org     0100

start   law     10          ; comment
        lac     undef       ; another comment
        hlt

        org     0200 + 1
start2  
        lac     0100        ; comment
        hlt
string  data    'ascii'

        end     start
