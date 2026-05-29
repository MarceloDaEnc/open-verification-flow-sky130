# open-verification-flow-sky130

Ambiente de verificação funcional e pós-layout para um transceptor UART implementado no PDK **sky130** da SkyWater Technology. O projeto combina uma infraestrutura UVM escrita em Python (via **pyuvm/cocotb**) com simuladores open-source e um fluxo de estimativa de consumo baseado em **LibreLane**.

---

## Índice

- [Visão Geral](#visão-geral)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Ambiente UVM](#ambiente-uvm)
- [Ferramentas Necessárias](#ferramentas-necessárias)
- [Como Executar](#como-executar)
- [Estimativa de Potência](#estimativa-de-potência)
- [Licença](#licença)

---

## Visão Geral

O repositório cobre todo o ciclo de verificação de um IP UART, desde a simulação RTL até a verificação pós-layout com anotação SDF, medição de cobertura de código e estimativa de potência com VCD real.

```
RTL  ──►  Simulação RTL (Icarus + cocotb/pyuvm)
     ──►  Cobertura de Código (Verilator + lcov)
     ──►  Síntese e P&R (LibreLane + ciel sky130)
          └──►  Netlist  ──►  Simulação Pós-Layout (Icarus + SDF)
                         ──►  Estimativa de Potência (OpenSTA via LibreLane)
```

---

## Estrutura do Repositório

```
open-verification-flow-sky130/
├── rtl/                          # RTL sintetizável
│   ├── impl_top.v                # Top-level do design
│   ├── uart_tx.v                 # Transmissor UART
│   └── uart_rx.v                 # Receptor UART
│
├── uvm/
│   ├── components/               # Biblioteca de verificação UVM (pyuvm)
│   │   ├── defs.py               # Parâmetros globais (BIT_RATE, CLK_HZ, FrameType…)
│   │   ├── seq_item.py           # UartSeqItem — item de transação
│   │   ├── bfm.py                # Bus Functional Model (interface com DUT via cocotb)
│   │   ├── driver.py             # Driver UVM
│   │   ├── monitor.py            # Monitor UVM
│   │   ├── agent.py              # Agent (Driver + Monitor + Sequencer)
│   │   ├── scoreboard.py         # Scoreboard (verificação automática)
│   │   ├── coverage.py           # Modelo de cobertura funcional
│   │   ├── seq.py                # Sequências (Sanity, Random, Coverage)
│   │   ├── env.py                # Ambiente top-level
│   │   └── test_uart.py          # Test cases cocotb
│   └── wrapper/
│       ├── uart_rtl_wrapper.v    # Wrapper para simulação RTL
│       └── uart_netlist_wrapper.v # Wrapper para simulação pós-layout
│
├── postlayout/                   # Artefatos gerados pelo P&R (LibreLane)
│   ├── gds/                      # Layout GDS
│   ├── nl/                       # Netlist mapeada
│   ├── pnl/                      # Netlist pós-roteamento
│   ├── spef/{min,nom,max}/       # Parasitas extraídos (3 corners)
│   ├── sdf/{corner}/             # Anotações de timing (SDF)
│   ├── lib/{corner}/             # Liberty caracterizado
│   ├── lef/                      # Abstração física
│   └── tech/                     # Modelos sky130 (primitives, .lib, .v)
│
└── scripts/
    ├── RTL_simulation/           # Makefile — simulação RTL (Icarus + cocotb)
    ├── code_coverage/            # Makefile — cobertura de código (Verilator)
    ├── netlist_simulation_with_SDF_annotation/
    │   ├── Makefile              # Simulação pós-layout com anotação SDF
    │   └── run_simulation.sh     # Script auxiliar (refatora SDF/NL e chama make)
    ├── power_estimation/
    │   ├── power_vcd.tcl         # Script OpenSTA de estimativa de potência
    │   └── run_power_script.sh   # Prepara artefatos e executa OpenSTA via Docker
    └── refactor/
        └── refactor.py           # Utilitário de refatoração de SDF/netlist
```

---

## Ambiente UVM

O ambiente de verificação segue a arquitetura UVM clássica, implementada inteiramente em Python com **pyuvm** e integrada ao simulador via **cocotb**.

```
┌─────────────────────────────────────────────────────┐
│  Env                                                │
│                                                     │
│  ┌──────────────────────────────────┐               │
│  │  Agent                           │               │
│  │  ┌──────────┐  ┌──────────────┐  │               │
│  │  │Sequencer │  │   Driver     │──┼──► driver_ap ──► Coverage
│  │  └──────────┘  └──────────────┘  │               │
│  │                ┌──────────────┐  │               │
│  │                │   Monitor    │──┼──► monitor_ap ──► Scoreboard.result
│  │                └──────────────┘  │               │
│  └──────────────────────────────────┘               │
│                                                     │
│  ┌─────────────┐   ┌──────────────┐                 │
│  │  Coverage   │   │  Scoreboard  │                 │
│  └─────────────┘   └──────────────┘                 │
└─────────────────────────────────────────────────────┘
```

| Componente    | Arquivo              | Responsabilidade                                          |
|---------------|----------------------|-----------------------------------------------------------|
| `Bfm`         | `bfm.py`             | Interface direta com os sinais do DUT via cocotb          |
| `Driver`      | `driver.py`          | Converte `UartSeqItem` em estímulos no barramento         |
| `Monitor`     | `monitor.py`         | Amostra a saída do DUT e publica no `monitor_ap`          |
| `Scoreboard`  | `scoreboard.py`      | Compara estímulo (cmd_export) × resposta (result_export)  |
| `Coverage`    | `coverage.py`        | Rastreia bins de cobertura funcional                      |
| `Agent`       | `agent.py`           | Agrega Driver, Monitor e Sequencer; expõe TLM ports       |
| `Env`         | `env.py`             | Instancia e conecta todos os componentes                  |
| Sequências    | `seq.py`             | `UartSanitySeq`, `UartRandomSeq`, `UartCoverageSeq`       |

**Conexões TLM:**

```
agent.driver_ap  → scoreboard.cmd_export
agent.driver_ap  → coverage.analysis_export
agent.monitor_ap → scoreboard.result_export
```

---

## Ferramentas Necessárias

| Ferramenta | Versão | Link de instalação |
|---|---|---|
| **Icarus Verilog** | `devel 13.0` | <https://github.com/steveicarus/iverilog> |
| **Verilator** | mais recente | <https://verilator.org/guide/latest/install.html> |
| **Python 3** | `3.12.4` | <https://www.python.org/downloads/release/python-3124/> |
| **cocotb** | mais recente | <https://docs.cocotb.org/en/stable/install.html> |
| **pyuvm** | mais recente | <https://github.com/pyuvm/pyuvm> |
| **LibreLane** | mais recente | <https://github.com/efabless/librelane> |
| **ciel (PDK sky130)** | mais recente | <https://github.com/efabless/ciel> |
| **Docker** | qualquer recente | <https://docs.docker.com/engine/install/> (necessário para estimativa de potência) |

### Instalação rápida das dependências Python

```bash
pip install cocotb pyuvm
```

---

## Como Executar

> Em todos os casos, execute os comandos a partir da raiz do repositório ou do diretório indicado.

### 1. Simulação RTL

Utiliza **Icarus Verilog** como simulador e o ambiente pyuvm/cocotb.

```bash
cd scripts/RTL_simulation
make
```

Os resultados ficam em `scripts/RTL_simulation/results.xml` e o log em `scripts/RTL_simulation/sim_build/`.

Para habilitar dump de forma de onda (FST), descomente `export WAVES = 1` no `Makefile`.

---

### 2. Cobertura de Código

Utiliza **Verilator** com instrumentação de cobertura e gera relatório HTML via `lcov`.

```bash
cd scripts/code_coverage
make
```

O relatório HTML é gerado em `scripts/code_coverage/relatorio_de_cobertura/index.html`.

---

### 3. Simulação Pós-Layout com Anotação SDF

Antes de executar, refatora os arquivos SDF e netlist para compatibilidade com Icarus Verilog:

```bash
cd scripts/netlist_simulation_with_SDF_annotation
bash run_simulation.sh
```

O script executa automaticamente:
1. `refactor.py` no SDF (`nom_tt_025C_1v80`)
2. `refactor.py` na netlist pós-layout
3. `make` com Icarus Verilog e as flags `-gspecify -ginterconnect -DSDF_DELAYS`

Alternativamente, após refatorar manualmente, basta:

```bash
cd scripts/netlist_simulation_with_SDF_annotation
make
```

---

### 4. Estimativa de Potência

Requer **Docker** com a imagem LibreLane disponível localmente. O script copia os artefatos necessários, executa o refator no SPEF e chama o OpenSTA via container.

```bash
cd scripts/power_estimation
bash run_power_script.sh
```

> **Pré-requisito:** é necessário ter gerado o arquivo `dump.vcd` a partir da simulação pós-layout (passo 3) antes de executar a estimativa de potência.

---

## Licença

Este projeto está licenciado conforme o arquivo [LICENSE](LICENSE).

---

*Desenvolvido na Universidade Federal de São Carlos (UFSCar) — Autor: Marcelo Rodrigues Soares*