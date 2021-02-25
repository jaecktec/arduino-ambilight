#!/bin/bash

# if the script has a parser error
# sed -i -e 's/\r$//' ./build_proto.sh

# run this one in the root folder, then you can run ./build_proto.sh if you don't want to install protobuf by urself
# docker run -it --rm -v ${PWD}:/workspace protoc:local /bin/bash
protoc --plugin=protoc-gen-nanopb=/nanopb/generator/protoc-gen-nanopb \
  -I.:/nanopb/generator/proto/google/protobuf \
  -I.:/nanopb/generator/proto \
  --nanopb_out=./arduino/include/ \
  --python_out=./pythonapp/ \
  ./proto/z_message.proto
