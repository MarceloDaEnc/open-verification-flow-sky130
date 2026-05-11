# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : driver.py
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# RELEASE HISTORY  VERSION  DATE        AUTHOR   DESCRIPTION
# 1.0              1.0      2025-07-20  marcelo  First Release
# -----------------------------------------------------------------------------
# KEYWORDS : UART, UVM, Driver, cocotb, pyuvm
# -----------------------------------------------------------------------------
# PURPOSE  : UVM Driver for the UART verification environment.
#            Retrieves UartSeqItems from the sequencer and delegates signal
#            driving to the BFM (send_byte). After each transaction the item
#            is broadcast on the analysis port so that the Scoreboard and
#            Coverage collector can record the stimulus.
# -----------------------------------------------------------------------------

from pyuvm import *
from .bfm import Bfm


class Driver(uvm_driver):
    """
    Pulls UartSeqItems from the sequencer and drives uart_rxd via the BFM.

    Analysis port (ap)
    ------------------
    Writes the completed UartSeqItem so that downstream subscribers
    (Scoreboard cmd_export, Coverage analysis_export) can record it.
    """

    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)

    def start_of_simulation_phase(self):
        self.bfm = Bfm()

    async def run_phase(self):
        while True:
            item = await self.seq_item_port.get_next_item()

            await self.bfm.send_byte(item)

            self.ap.write(item)
            self.seq_item_port.item_done()
