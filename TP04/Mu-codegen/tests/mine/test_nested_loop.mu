var x,y:int;
x=1;

while x <= 10 {
	
	x=x+1;

	log(x);

	if x > 5 {
		
		if x <= 7 {
			log(0);	
		}
		else {
			log(1);
		}
	}
}

# EXPECTED
# 2
# 3
# 4
# 5
# 6
# 0
# 7
# 0
# 8
# 1
# 9
# 1
# 10
# 1
# 11
# 1
