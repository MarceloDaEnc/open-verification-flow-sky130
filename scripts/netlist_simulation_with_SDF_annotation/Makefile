# Makefile
export PYTHONPATH := $(PWD)/../uvm/wrapper
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += 	$(PWD)/../postlayout/netlist/impl_top_nl_refactored.v \
					$(PWD)/../uvm/wrapper/uart_wrapper.v\
					$(PWD)/../postlayout/tech/*.v

TOPLEVEL = uart_tb_wrapper
MODULE = tests.test_uart

# Compilation arguments for Icarus Verilog
COMPILE_ARGS += -gspecify -ginterconnect
COMPILE_ARGS += -DUNIT_DELAY=\#1 -DSKY130_FD_SC_HD__LPFLOW_BLEEDER_1_TIMING_V -DSDF_DELAYS

# Specify log file for simulation output
SIM_LOG_FILE = $(PWD)/testbench.log

# Enable VCD waveform dump
export WAVES = 1

# Include Cocotb simulation rules
include $(shell cocotb-config --makefiles)/Makefile.sim