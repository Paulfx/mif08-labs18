var n:int;
var s:bool;
s=false;
n=10;
if s && n - 8 < 2 {
	log(2);
} else if !s {
	log(s);
} else {
	log(3);
}

if s {
	log(4);
} else {
	log(5);
}

# EXPECTED
# 0
# 5