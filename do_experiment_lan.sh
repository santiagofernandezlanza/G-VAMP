# Copyright 2020 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FECHA=$(date +%Y%m%d_%H%M%S)

TRAIN=IOB
#TRAIN=IOB_Deep-BGT
#TRAIN=gappy-1_Deep-BGT
#TRAIN=gappy-crossy_Deep-BGT

DEV=IOB
#DEV=IOB_Deep-BGT
#DEV=gappy-1_Deep-BGT
#DEV=gappy-crossy_Deep-BGT

TEST=IOB
#TEST=IOB_Deep-BGT
#TEST=gappy-1_Deep-BGT
#TEST=gappy-crossy_Deep-BGT

#METHOD_FOR_SHARED=SIMPLE
METHOD_FOR_SHARED=SPLIT\&MERGE_OVL
PREPROCESS_ACTION=PRE::train_$TRAIN:dev_$DEV:test_$TEST:$METHOD_FOR_SHARED
CORPUS_VERSION=$1
LAN=$2
counter=0
MODEL=google-bert/bert-base-multilingual-cased
#MODEL=dvilares/bertinho-gl-base-cased
#MODEL=models/litlat-bert/
#MODEL=models/bert-ro
#MODEL=models/sloberta
SEED_1=1
SEED_2=2
SEED_3=3
#MAX_SENT_LENGHT=512
#MAX_SENT_LENGHT=4096
MAX_SENT_LENGHT=Null
INCREMENTAL=NO
PROCESS_ACTION=PRO::model_$MODEL:seeds_$SEED_1-$SEED_2-$SEED_3:length_$MAX_SENT_LENGHT:inc_$INCREMENTAL

#export CUDA_VISIBLE_DEVICES=0

if [ -d "models/$LAN" ]
then
        if [ "$(ls -A models/$LAN)" ]; then
                MODEL=$(ls -d models/$LAN/* | head -n 1)
        fi
else
        echo "Directory models/$LAN not found."
fi

echo "*************************************************************************************"
echo "*************************************************************************************"
echo "*************************************************************************************"
echo "*************************************************************************************"
echo "******* SELECTED MODEL: "$MODEL
echo "*************************************************************************************"
echo "*************************************************************************************"
echo "*************************************************************************************"
echo "*************************************************************************************"

./preprocess.sh $CORPUS_VERSION $LAN $TRAIN $DEV $TEST $METHOD_FOR_SHARED

mv corpus/$CORPUS_VERSION/$LAN/preprocess/train.json corpus/$CORPUS_VERSION/$LAN/preprocess/train_0.json

mkdir evaluations/$FECHA-$CORPUS_VERSION-$LAN

mkdir evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_1
mkdir evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_1/predictions
mkdir evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_1/postprocess
for file in corpus/$CORPUS_VERSION/$LAN/preprocess/train*
do
  echo "Processing $file $counter"
  ./process.sh $MODEL $SEED_1 $LAN _$counter $MAX_SENT_LENGHT $CORPUS_VERSION
  cp /tmp/test-ner/predictions.txt evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_1/predictions/$counter.txt
  ./delete_process.sh
  ((counter++))
done
python3 source/postprocess.py corpus/$CORPUS_VERSION/$LAN/ evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_1/predictions/ $METHOD_FOR_SHARED
cp corpus/$CORPUS_VERSION/$LAN/postprocess/*.cupt evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_1/postprocess
DESTINO="evaluations/$FECHA-$CORPUS_VERSION-$LAN/eval_$SEED_1.txt"
source/$CORPUS_VERSION/evaluate.sh $CORPUS_VERSION $LAN > $DESTINO

counter=0
mkdir evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_2
mkdir evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_2/predictions
mkdir evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_2/postprocess
for file in corpus/$CORPUS_VERSION/$LAN/preprocess/train*
do
  echo "Processing $file $counter"
  ./process.sh $MODEL $SEED_2 $LAN _$counter $MAX_SENT_LENGHT $CORPUS_VERSION
  cp /tmp/test-ner/predictions.txt evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_2/predictions/$counter.txt
  ./delete_process.sh
  ((counter++))
done
python3 source/postprocess.py corpus/$CORPUS_VERSION/$LAN/ evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_2/predictions/ $METHOD_FOR_SHARED
cp corpus/$CORPUS_VERSION/$LAN/postprocess/*.cupt evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_2/postprocess
DESTINO="evaluations/$FECHA-$CORPUS_VERSION-$LAN/eval_$SEED_2.txt"
source/$CORPUS_VERSION/evaluate.sh $CORPUS_VERSION $LAN > $DESTINO

counter=0
mkdir evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_3
mkdir evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_3/predictions
mkdir evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_3/postprocess
for file in corpus/$CORPUS_VERSION/$LAN/preprocess/train*
do
  echo "Processing $file $counter"
  ./process.sh $MODEL $SEED_3 $LAN _$counter $MAX_SENT_LENGHT $CORPUS_VERSION
  cp /tmp/test-ner/predictions.txt evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_3/predictions/$counter.txt
  ./delete_process.sh
  ((counter++))
done
python3 source/postprocess.py corpus/$CORPUS_VERSION/$LAN/ evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_3/predictions/ $METHOD_FOR_SHARED
cp corpus/$CORPUS_VERSION/$LAN/postprocess/*.cupt evaluations/$FECHA-$CORPUS_VERSION-$LAN/$SEED_3/postprocess
DESTINO="evaluations/$FECHA-$CORPUS_VERSION-$LAN/eval_$SEED_3.txt"
source/$CORPUS_VERSION/evaluate.sh $CORPUS_VERSION $LAN > $DESTINO

./build_readme.sh evaluations/$FECHA-$CORPUS_VERSION-$LAN $PREPROCESS_ACTION $PROCESS_ACTION $LAN $CORPUS_VERSION

#cp corpus/$CORPUS_VERSION/$LAN/preprocess/README* evaluations/$FECHA-$CORPUS_VERSION-$LAN

cat evaluations/$FECHA-$CORPUS_VERSION-$LAN/README_evaluations.txt

