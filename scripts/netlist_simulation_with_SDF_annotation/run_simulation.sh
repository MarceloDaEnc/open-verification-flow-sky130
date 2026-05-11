make clean

cd ../../postlayout/sdf/

python3 ../../scripts/refactor/refactor.py ./nom_tt_025C_1v80/impl_top__nom_tt_025C_1v80.sdf

cd ../nl

python3 ../../scripts/refactor/refactor.py impl_top.nl.v

cd ../../scripts/netlist_simulation_with_SDF_annotation

make