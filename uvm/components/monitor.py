# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : monitor.py
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# RELEASE HISTORY  VERSION  DATE        AUTHOR   DESCRIPTION
# 1.0              1.0      2025-07-20  marcelo  First Release
# -----------------------------------------------------------------------------
# KEYWORDS : UART, UVM, Monitor, cocotb, pyuvm
# -----------------------------------------------------------------------------
# PURPOSE  : UVM Monitor for the UART verification environment.
#            Passively observes uart_txd (the DUT's loopback echo output) and
#            forwards decoded (data, stop_ok) tuples to its analysis port.
#            All signal-level decoding is delegated to the BFM, keeping this
#            component free of cocotb primitives.
# -----------------------------------------------------------------------------

from pyuvm import *
from .bfm import Bfm


class Monitor(uvm_component):
    """
    Observes the DUT's uart_txd output and writes decoded frames to ap.

    Analysis port (ap)
    ------------------
    Writes tuples of (received_byte: int, stop_ok: bool) for each frame
    detected on uart_txd by the BFM's monitor_txd task.
    """

    def __init__(self, name, parent):
        super().__init__(name, parent)

    def build_phase(self):
        self.ap  = uvm_analysis_port("ap", self)
        self.bfm = Bfm()

    async def run_phase(self):
        self.bfm.logger = self.logger
        await self.bfm.monitor_txd(self.ap)
