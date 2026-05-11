# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : env.py
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# RELEASE HISTORY  VERSION  DATE        AUTHOR   DESCRIPTION
# 1.0              1.0      2025-07-20  marcelo  First Release
# -----------------------------------------------------------------------------
# KEYWORDS : UART, UVM, Environment, cocotb, pyuvm
# -----------------------------------------------------------------------------
# PURPOSE  : Top-level UVM environment for the UART verification.
#            Instantiates and connects all verification components.
#
# Component graph:
#
#   ┌─────────────────────────────────────────────────────────┐
#   │  Env                                                    │
#   │                                                         │
#   │  ┌────────────────────────────────┐                     │
#   │  │  Agent                         │                     │
#   │  │  ┌──────────┐  ┌────────────┐  │  driver_ap ──►  Coverage
#   │  │  │ Sequencer│  │  Driver    │  │                     │
#   │  │  └──────────┘  └────────────┘  │  driver_ap ──►  Scoreboard.cmd
#   │  │                ┌────────────┐  │                     │
#   │  │                │  Monitor   │  │  monitor_ap ──► Scoreboard.result
#   │  │                └────────────┘  │                     │
#   │  └────────────────────────────────┘                     │
#   │                                                         │
#   │  ┌─────────────┐   ┌─────────────┐                      │
#   │  │  Coverage   │   │  Scoreboard │                      │
#   │  └─────────────┘   └─────────────┘                      │
#   └─────────────────────────────────────────────────────────┘
#
# TLM connections:
#   agent.driver_ap  → scoreboard.cmd_export
#   agent.driver_ap  → coverage.analysis_export
#   agent.monitor_ap → scoreboard.result_export
# -----------------------------------------------------------------------------

from pyuvm import *
from .agent      import Agent
from .scoreboard import Scoreboard
from .coverage   import Coverage


class Env(uvm_env):
    """
    Top-level environment — instantiates Agent, Scoreboard and Coverage,
    then wires their TLM analysis ports together.
    """

    def build_phase(self):
        self.agent      = Agent.create("agent", self)
        self.coverage   = Coverage.create("coverage", self)
        self.scoreboard = Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        # Make the sequencer reachable from test classes via ConfigDB
        ConfigDB().set(None, "*", "SEQR", self.agent.seqr)

        # Stimulus (from driver) goes to both Scoreboard and Coverage
        self.agent.driver_ap.connect(self.scoreboard.cmd_export)
        self.agent.driver_ap.connect(self.coverage.analysis_export)

        # Observations (from monitor) go to Scoreboard result side
        self.agent.monitor_ap.connect(self.scoreboard.result_export)
