module dump();
    initial begin
        $dumpfile ("strobe_gen.vcd");
        $dumpvars (0, strobe_gen);
        #1;
    end
endmodule
