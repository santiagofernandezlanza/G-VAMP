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


if [ "$5" != "Null" ]; then
  MAX_LEN_ARG=--max_seq_length=$5
else
  MAX_LEN_ARG=""
fi


python3 transformers/examples/pytorch/token-classification/run_ner.py \
  --model_name_or_path $1 \
  --train_file corpus/$6/$3/preprocess/train$4.json \
  --validation_file corpus/$6/$3/preprocess/dev.json \
  --test_file corpus/$6/$3/preprocess/test.json \
  --output_dir /tmp/test-ner \
  --do_train \
  --do_predict \
  --do_eval \
  --trust_remote_code=True \
  --overwrite_cache=True \
  --eval_strategy=epoch \
  --save_strategy=epoch \
  --load_best_model_at_end=True \
  --num_train_epochs=15 \
  --metric_for_best_model=eval_f1\
  --seed $2 $MAX_LEN_ARG
