# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : agent.py
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# RELEASE HISTORY  VERSION  DATE        AUTHOR   DESCRIPTION
# 1.0              1.0      2025-07-20  marcelo  First Release
# -----------------------------------------------------------------------------
# KEYWORDS : UART, UVM, Agent, cocotb, pyuvm
# -----------------------------------------------------------------------------
# PURPOSE  : UVM Agent for the UART verification environment.
#            Encapsulates the sequencer, driver and monitor into a single
#            reusable verification component.  Exposes two analysis ports
#            (driver_ap, monitor_ap) so that Env can wire them to the
#            Scoreboard and Coverage without depending on internal structure.
#
# TLM connections built inside this agent:
#   driver.seq_item_port  →  seqr.seq_item_export
# Ports exposed to Env:
#   driver_ap  (alias for driver.ap)  — carries UartSeqItem (stimulus)
#   monitor_ap (alias for monitor.ap) — carries (data, stop_ok) tuples
# -----------------------------------------------------------------------------

from pyuvm import *
from .driver  import Driver
from .monitor import Monitor


class Agent(uvm_agent):
    """
    Encapsulates the sequencer, driver and monitor for the UART interface.
    """

    def build_phase(self):
        self.seqr    = uvm_sequencer.create("seqr", self)
        self.driver  = Driver.create("driver", self)
        self.monitor = Monitor.create("monitor", self)

    def connect_phase(self):
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)

        # Re-export analysis ports for Env to wire downstream
        self.driver_ap  = self.driver.ap
        self.monitor_ap = self.monitor.ap
