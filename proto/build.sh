#!/bin/bash
protoc --plugin=protoc-gen-nanopb=/nanopb/generator/protoc-gen-nanopb --python_out=./pythonapp --nanopb_out=./arduino/src proto/z_message.proto