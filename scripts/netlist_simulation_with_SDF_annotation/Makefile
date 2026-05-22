# Makefile
export PYTHONPATH := $(CURDIR)/../../uvm/:$(CURDIR)/../../uvm/wrapper:$(PYTHONPATH)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += 	$(CURDIR)/../../postlayout/nl/impl_top_nl_refactored.v \
					$(CURDIR)/../../uvm/wrapper/uart_netlist_wrapper.v\
					$(CURDIR)/../../postlayout/tech/*.v

TOPLEVEL = uart_rtl_wrapper
COCOTB_TEST_MODULES = components.test_uart

# Compilation arguments for Icarus Verilog
COMPILE_ARGS += -gspecify -ginterconnect
COMPILE_ARGS += -DUNIT_DELAY=\#1 -DSKY130_FD_SC_HD__LPFLOW_BLEEDER_1_TIMING_V -DSDF_DELAYS

# Specify log file for simulation output
SIM_LOG_FILE = $(CURDIR)/testbench.log

# Enable VCD waveform dump
# export WAVES = 1

# Include Cocotb simulation rules
include $(shell cocotb-config --makefiles)/Makefile.sim