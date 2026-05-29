cp ../../postlayout/tech/sky130_fd_sc_hd__tt_025C_1v80.lib .
cp ../../postlayout/nl/impl_top_nl_refactored.v .
cp ../../postlayout/sdc/impl_top.sdc .

cd ../../postlayout/spef

python3 ../../scripts/refactor/refactor.py ./nom/impl_top.nom.spef

cd ../../scripts/power_estimation

cp ../../postlayout/spef/nom/impl_top_nom_refactored.spef .

cp ../../postlayout/sdc/impl_top.sdc .

cp ../netlist_simulation_with_SDF_annotation/dump.vcd .

IMAGE_NAME=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "librelane" | head -n 1)

if [ -z "$IMAGE_NAME" ]; then
    echo "Error: Librelane image not found!"
    exit 1
fi

docker run --rm -v $(pwd):/openlane -w /openlane "$IMAGE_NAME" sta power_vcd.tcl

