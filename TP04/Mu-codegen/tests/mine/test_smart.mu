var a,b,c,d,e,f,g,h:int;
var boolTrue,boolFalse:bool;
boolTrue = true;
boolFalse = false;
a = 0;
b = 0;
c = 0;
d = 0;
e = 0;
f = 0;
g = 0;
h = 0;

if (true) {
    b = a + 10; #10
} else {
  boolTrue = false;
}
if (false) {
  boolFalse = true;
} else {
  c = b + 4; #14
}
if (c == 14) {
  d = c * 2; #28
}
if (d == 28) {
  d = d + 1; #29
} else {
  e = 100;
}
if (e < 90) {
  f = e + 35; #35
}

g = f - 10; #25
h = g + 40; #65

log(a);
log(b);
log(c);
log(d);
log(e);
log(f);
log(g);
log(h);
log(boolTrue);
log(boolFalse);

# EXPECTED
# 0
# 10
# 14
# 29
# 0
# 35
# 25
# 65
# 1
# 0