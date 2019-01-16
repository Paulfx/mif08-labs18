grammar Tutu;

prog: EOF {print("Sujet B!");} ;


WS : [ \t\r\n]+ -> skip ; // skip spaces, tabs, newlines
