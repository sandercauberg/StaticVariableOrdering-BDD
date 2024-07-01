module alu4_cl(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p);
input
  a,
  b,
  c,
  d,
  e,
  f,
  g,
  h,
  i,
  j;
output
  k,
  l,
  m,
  n,
  o,
  p;
wire
  \[26] ,
  h1,
  \[27] ,
  i1,
  \[28] ,
  j1,
  \[29] ,
  k0,
  k1,
  \[10] ,
  l1,
  \[11] ,
  \[12] ,
  n0,
  \[13] ,
  \[48] ,
  \[49] ,
  \[0] ,
  \[15] ,
  \[30] ,
  \[1] ,
  \[16] ,
  r0,
  \[31] ,
  \[2] ,
  \[17] ,
  s0,
  \[3] ,
  \[18] ,
  t1,
  \[33] ,
  \[4] ,
  \[19] ,
  u1,
  \[34] ,
  \[5] ,
  \[35] ,
  \[6] ,
  \[50] ,
  w0,
  \[36] ,
  \[7] ,
  \[37] ,
  \[8] ,
  y1,
  \[38] ,
  \[9] ,
  z1,
  \[20] ,
  b2,
  \[21] ,
  c2,
  \[22] ,
  \[23] ,
  e0,
  e1,
  \[24] ,
  f0,
  f1,
  \[25] ;
assign
  \[26]  = ~f0 | i,
  h1 = f & e,
  \[27]  = ~l1 | ~a,
  i1 = ~f & ~e,
  \[28]  = ~k1 | ~a,
  j1 = ~f & e,
  \[29]  = \[24]  & ~c2,
  k0 = (\[19]  & (h1 & (w0 & b))) | ((\[19]  & (i1 & ~w0)) | ((\[34]  & \[3] ) | ((u1 & w0) | (u1 & b)))),
  k1 = (~\[27]  & (\[19]  & h1)) | ((\[19]  & (i1 & ~l1)) | ((\[34]  & f1) | u1)),
  \[10]  = f1 | ~c,
  l1 = (~\[10]  & (~z1 & (y1 & (~i1 & ~h1)))) | ((\[48]  & (~z1 & (~y1 & ~j1))) | ((\[49]  & (n0 & j)) | ((c2 & (i1 & f1)) | ((b2 & (~e & ~a)) | ((y1 & (j1 & a)) | (z1 & ~c)))))),
  \[11]  = (~s0 & w0) | (s0 & ~w0),
  k = \[0] ,
  l = \[1] ,
  m = \[2] ,
  n = \[3] ,
  o = \[4] ,
  p = \[5] ,
  \[12]  = j & h,
  n0 = f & ~e,
  \[13]  = (~y1 & (i1 & j)) | (\[23]  & ~h1),
  \[48]  = \[12]  & f1,
  \[49]  = ~f1 & a,
  \[0]  = (~\[10]  & (~z1 & (~h1 & (~j & h)))) | ((~\[36]  & (~\[21]  & (l1 & ~j))) | ((~j1 & (f1 & (~j & h))) | ((\[49]  & (\[36]  & ~y1)) | ((\[38]  & (~\[35]  & a)) | ((\[36]  & (\[35]  & ~c)) | ((\[36]  & (~\[20]  & l1)) | ((\[35]  & (\[21]  & n0)) | ((~f0 & (j & ~i)) | ((\[20]  & ~l1) | ((f0 & i) | \[50] )))))))))),
  \[15]  = (\[25]  & t1) | (\[22]  & a),
  \[30]  = ~\[2]  | d,
  \[1]  = (~\[36]  & (w0 & (~\[2]  & ~j))) | ((~b2 & (\[3]  & (~j & h))) | ((n0 & (~j & (h & d))) | ((\[38]  & (~\[35]  & b)) | ((\[36]  & (\[35]  & ~d)) | ((\[36]  & (\[33]  & ~y1)) | ((\[36]  & (~\[20]  & w0)) | ((\[35]  & (n0 & \[2] )) | ((b2 & (i1 & h)) | ((~\[26]  & ~e0) | ((\[26]  & e0) | ((\[20]  & ~w0) | \[50] ))))))))))),
  \[16]  = \[18]  & l1,
  r0 = j1 & ~g,
  \[31]  = 0,
  \[2]  = (~d & ~b) | \[3] ,
  \[17]  = (\[23]  & (~b & ~a)) | (\[6]  & (~k1 & ~k0)),
  s0 = (u1 & (\[3]  & ~g)) | (\[34]  & ~k0),
  \[3]  = d & b,
  \[18]  = \[6]  & j1,
  t1 = (u1 & (f1 & ~g)) | (\[34]  & ~k1),
  \[33]  = r0 & ~\[2] ,
  \[4]  = (~\[25]  & (\[12]  & (e1 & (~h1 & w0)))) | ((\[37]  & (~y1 & (h1 & j))) | ((\[12]  & (~y1 & (~h1 & \[3] ))) | ((\[12]  & (~h1 & (~e0 & b))) | ((\[37]  & (\[6]  & n0)) | ((~\[28]  & (\[15]  & k0)) | ((\[6]  & (~e0 & ~f)) | ((\[48]  & \[33] ) | ((~\[26]  & e0) | ((\[17]  & h1) | (s0 & w0)))))))))),
  \[19]  = c2 & j,
  u1 = \[12]  & n0,
  \[34]  = \[19]  & j1,
  \[5]  = \[21]  & \[2] ,
  \[35]  = c2 & ~y1,
  \[6]  = c2 & y1,
  \[50]  = \[29]  & h1,
  w0 = (~\[23]  & (\[12]  & (~z1 & (~j1 & \[3] )))) | ((\[19]  & (~\[10]  & (n0 & \[2] ))) | ((\[19]  & (\[10]  & (n0 & ~\[2] ))) | ((\[30]  & (y1 & j1)) | ((\[23]  & (i1 & a)) | ((c2 & (i1 & \[3] )) | ((b2 & (~e & ~b)) | (z1 & ~d))))))),
  \[36]  = ~j & ~f,
  \[7]  = (~s0 & k0) | (s0 & ~k0),
  \[37]  = e1 & ~l1,
  \[8]  = (~k0 & b) | (k0 & ~b),
  y1 = (~j & (~h & ~g)) | (j & g),
  \[38]  = ~y1 & g,
  \[9]  = (\[12]  & (~y1 & h1)) | (\[6]  & n0),
  z1 = (\[38]  & (j1 & h)) | ((~c2 & (n0 & j)) | (c2 & h1)),
  \[20]  = (\[38]  & i1) | (y1 & r0),
  b2 = (\[36]  & ~g) | (y1 & ~j),
  \[21]  = ~\[49]  & \[10] ,
  c2 = ~h & g,
  \[22]  = i1,
  \[23]  = y1 & h,
  e0 = (\[28]  & (~\[23]  & (~k0 & (w0 & (l1 & j))))) | ((\[24]  & (~\[17]  & (\[11]  & (~t1 & (~i1 & ~h1))))) | ((~\[18]  & (y1 & (e1 & (j & (b & a))))) | ((\[28]  & (\[24]  & (~\[18]  & (~\[9]  & \[8] )))) | ((\[48]  & (\[37]  & (~\[33]  & ~y1))) | ((~\[48]  & (\[33]  & j)) | ((\[25]  & (\[7]  & ~t1)) | ((\[18]  & (\[11]  & ~l1)) | ((\[13]  & (~e1 & ~b)) | ((\[13]  & (e1 & b)) | ((\[37]  & \[9] ) | (\[17]  & h1))))))))))),
  e1 = (~\[27]  & w0) | (\[27]  & ~w0),
  \[24]  = j & ~h,
  f0 = (~\[13]  & (~\[9]  & (~t1 & (~h1 & (l1 & j))))) | ((~\[49]  & (~\[16]  & (~\[9]  & \[6] ))) | ((\[49]  & (~y1 & j)) | ((\[23]  & (h1 & ~a)) | ((\[23]  & (l1 & ~a)) | ((\[13]  & (~l1 & a)) | ((~\[10]  & (r0 & j)) | ((\[29]  & a) | (\[9]  & ~l1)))))))),
  f1 = c & a,
  \[25]  = ~y1 & u1;
endmodule

