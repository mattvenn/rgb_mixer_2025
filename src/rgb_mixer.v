`default_nettype none
`timescale 1ns/1ns
module rgb_mixer (
    input clk,
    input reset_n,
    input enc0_a,
    input enc0_b,
    input enc1_a,
    input enc1_b,
    input enc2_a,
    input enc2_b,
    output pwm0_out,
    output pwm1_out,
    output pwm2_out
);
    wire reset = ! reset_n;

    // array of 3 encoder registers
    wire [7:0] enc [CHANNELS-1:0];

    // array of 3 encoder channels
    wire enc_a [CHANNELS-1:0];
    wire enc_b [CHANNELS-1:0];

    // assign all the inputs
    assign enc_a[0] = enc0_a;
    assign enc_b[0] = enc0_b;
    assign enc_a[1] = enc1_a;
    assign enc_b[1] = enc1_b;
    assign enc_a[2] = enc2_a;
    assign enc_b[2] = enc2_b;

    // array of intermediate wires
    wire enc_a_db [CHANNELS-1:0];
    wire enc_b_db [CHANNELS-1:0];
    wire pwm_out [CHANNELS-1:0];

    // assign outputs
    assign pwm0_out = pwm_out[0];
    assign pwm1_out = pwm_out[1];
    assign pwm2_out = pwm_out[2];

    localparam CHANNELS = 3;
    generate
        genvar i;
        for(i = 0; i < CHANNELS; i = i + 1) begin : channel
    
            // debouncers, 2 for each encoder
            debounce #(.HIST_LEN(8)) debounce_a(.clk(clk), .reset(reset), .button(enc_a[i]), .debounced(enc_a_db[i]));
            debounce #(.HIST_LEN(8)) debounce_b(.clk(clk), .reset(reset), .button(enc_b[i]), .debounced(enc_b_db[i]));

            // encoders
            encoder #(.WIDTH(8)) encoder(.clk(clk), .reset(reset), .a(enc_a_db[i]), .b(enc_b_db[i]), .value(enc[i]));

            // pwm modules
            pwm #(.WIDTH(8)) pwm(.clk(clk), .reset(reset), .out(pwm_out[i]), .level(enc[i]));
        end
    endgenerate

endmodule
