grammar Palin;

prog: EOF {print("Sujet A!");} ;


WS : [ \t\r\n]+ -> skip ; // skip spaces, tabs, newlines
