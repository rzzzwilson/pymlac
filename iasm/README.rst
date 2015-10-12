Imlac Assembler (iasm)
======================

The code here is an Imlac assembler that takes an Imlac assembler file and
generates a patertape file including the bootstrap loader.  Optionally,
a listing file can also be produced.

    Usage: iasm <option> <filename>                                           
    
    where <option>   is zero or more of                                       
                       -bptr        use a papertape boot loader                  
                       -btty        use a teletype boot loader                   
                       -l <file>    write listing to file <file>                 
          <filename> is the file to assemble.                                 
    
    The input filename has the form of 'file.asm' and                         
    the output file will be 'file.ptp' or 'file.tty'.                         
