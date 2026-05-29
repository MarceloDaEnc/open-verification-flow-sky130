read_liberty sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog impl_top_nl_refactored.v
link_design impl_top
read_sdc impl_top.sdc
read_spef impl_top_nom_refactored.spef
read_vcd -scope uart_rtl_wrapper/dut dump.vcd
report_power
exit
