`timescale 1 ns / 1ps

module uart_rtl_wrapper;

wire clk; 
wire sw_0; 
wire sw_1; 
wire uart_rxd; 
wire uart_txd; 
wire [7:0] led;

impl_top dut(
    .clk(clk),
    .sw_0(sw_0),
    .sw_1(sw_1),
    .uart_rxd(uart_rxd),
    .uart_txd(uart_txd),
    .led(led)
);

initial begin
    $sdf_annotate("../../postlayout/sdf/nom_tt_025C_1v80/impl_top__nom_tt_025C_1v80_refactored.sdf", dut);
end

initial begin
    $dumpvars(0);
end

endmodule