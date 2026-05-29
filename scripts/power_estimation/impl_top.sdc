###############################################################################
# Created by write_sdc
###############################################################################
current_design impl_top
###############################################################################
# Timing Constraints
###############################################################################
create_clock -name clk -period 25.0000 [get_ports {clk}]
set_clock_transition 0.1500 [get_clocks {clk}]
set_clock_uncertainty 0.2500 clk
set_propagated_clock [get_clocks {clk}]
set_input_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {sw_0}]
set_input_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {sw_1}]
set_input_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {uart_rxd}]
set_output_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {led[0]}]
set_output_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {led[1]}]
set_output_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {led[2]}]
set_output_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {led[3]}]
set_output_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {led[4]}]
set_output_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {led[5]}]
set_output_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {led[6]}]
set_output_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {led[7]}]
set_output_delay 5.0000 -clock [get_clocks {clk}] -add_delay [get_ports {uart_txd}]
###############################################################################
# Environment
###############################################################################
set_load -pin_load 0.0334 [get_ports {uart_txd}]
set_load -pin_load 0.0334 [get_ports {led[7]}]
set_load -pin_load 0.0334 [get_ports {led[6]}]
set_load -pin_load 0.0334 [get_ports {led[5]}]
set_load -pin_load 0.0334 [get_ports {led[4]}]
set_load -pin_load 0.0334 [get_ports {led[3]}]
set_load -pin_load 0.0334 [get_ports {led[2]}]
set_load -pin_load 0.0334 [get_ports {led[1]}]
set_load -pin_load 0.0334 [get_ports {led[0]}]
set_driving_cell -lib_cell sky130_fd_sc_hd__inv_2 -pin {Y} -input_transition_rise 0.0000 -input_transition_fall 0.0000 [get_ports {clk}]
set_driving_cell -lib_cell sky130_fd_sc_hd__inv_2 -pin {Y} -input_transition_rise 0.0000 -input_transition_fall 0.0000 [get_ports {sw_0}]
set_driving_cell -lib_cell sky130_fd_sc_hd__inv_2 -pin {Y} -input_transition_rise 0.0000 -input_transition_fall 0.0000 [get_ports {sw_1}]
set_driving_cell -lib_cell sky130_fd_sc_hd__inv_2 -pin {Y} -input_transition_rise 0.0000 -input_transition_fall 0.0000 [get_ports {uart_rxd}]
###############################################################################
# Design Rules
###############################################################################
set_max_transition 1.0000 [current_design]
set_max_capacitance 0.2000 [current_design]
set_max_fanout 16.0000 [current_design]
