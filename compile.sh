#!/bin/bash
ant real-clean
ant
sed -i 's/GenCopy/MarkSweep/' .ant.properties
ant
sed -i 's/MarkSweep/GenMS/' .ant.properties
ant
sed -i 's/GenMS/SemiSpace/' .ant.properties
ant
sed -i 's/SemiSpace/RefCount/' .ant.properties
ant
sed -i 's/RefCount/GenRC/' .ant.properties
ant
sed -i 's/GenRC/GenCopy/' .ant.properties
