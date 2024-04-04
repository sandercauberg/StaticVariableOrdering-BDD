module my_circuit(N1, N2, N3, N4, N5, output_wire);

input N1, N2, N3, N4, N5;
output output_wire;

assign output_wire = N1 ^ N2 ^ N3 ^ N4 ^ N5;

endmodule