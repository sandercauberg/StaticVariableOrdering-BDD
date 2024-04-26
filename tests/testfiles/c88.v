// Verilog
// c880
// Ninputs 60
// Noutputs 26
// NtotalGates 383
// OR2 29
// NOT1 63
// NOR2 61
// BUFF1 26

module c880 (N1,N8,N13,N17,N880,N881);

input N1,N8,N13,N17;

output N880, N881;

wire N269,N270,N273;

not NOT1_29 (N269, N1);
and AND2_1 (N270, N1, N269);
and AND2_2 (N273, N270, N8);
buf BUFF1_79 (N880, N273);
buf BUFF1_80 (N881, N17);

endmodule