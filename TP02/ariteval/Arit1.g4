grammar Arit1;

// MIF08@Lyon1 and CAP@ENSL, simple arit evaluator with semantic actions

prog:
      statement+ EOF
    ;

statement:
      expr SCOL    {print($expr.text+" = "+str($expr.val))} //prints the value              
    ;

expr returns [int val]:
	e1=expr MULT  e2=expr {$val=$e1.val*$e2.val} // MULT is *!
    | e1=expr PLUS  e2=expr {$val=$e1.val+$e2.val} // PLUS is + !
    | a=atom {$val=$a.val} //just copy!
    ;

atom returns [int val]:
      INT               {$val = int($INT.text)} //the parsed value        
    | '(' expr ')'      {$val=$expr.val} //just copy!
    ;


SCOL :      ';';
PLUS :      '+';
MINUS :     '-';
MULT :      '*';
DIV :       '/';

INT:        [0-9]+;

COMMENT
 : '#' ~[\r\n]* -> skip
 ;


NEWLINE:    '\r'? '\n' -> skip;
WS  :       (' '|'\t')+  -> skip;
