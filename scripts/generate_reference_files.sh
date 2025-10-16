#!/bin/bash
READER=raman
NXDL=NXraman

function update_witec_ref {
  cd witec/
  echo "Update WITec reference files"
  dataconverter Si-wafer-Raman-Spectrum-1.txt  eln_data.yaml --reader $READER --nxdl $NXDL --output example.nxs &> ref_output.txt
  cd ..
}

function update_rod_ref {
  cd rod/
  echo "Update rod reference files"
  dataconverter rod_file_1000679.rod --reader $READER --nxdl $NXDL --output example.nxs &> ref_output.txt
  cd ..
}

project_dir=$(dirname $(dirname $(realpath $0)))
cd $project_dir/tests/data

update_witec_ref
update_rod_ref
