#!/bin/bash
#
# Start up the EDR generator and send data to kafka topic(s)
# Assume that the kafka configuration is supplied as kafka.config
# Assume kafka topic names are $EDR_FLOW_TOPIC and $EDR_HTTP_TOPIC


# set up named pipes

mknod -p ${EDR_FLOW_PREFIX:=edr_flow_pipe}
mknod -p ${EDR_HTTP_PREFIX:=edr_http_pipe}

# pipe data to topics - running in background

# TODO: allow either topic to be skipped

nohup $SHELL "cat $EDR_FLOW_PREFIX | kafkacat -P -F kafka.config -t ${EDR_FLOW_TOPIC:=edr_flow}" & 
nohup $SHELL "cat $EDR_HTTP_PREFIX | kafkacat -P -F kafka.config -t ${EDR_HTTP_TOPIC:=edr_http}" &

# start the data generator

: ${EDR_START_EPOCH:=`date +%s`}
: ${EDR_END_EPOCH:=$(eval $EDR_START_EPOCH + 600)}

# and start the data generator
python datagen.py \
   --start_time $EDR_START_EPOCH --end_time $EDR_END_EPOCH \
   --write_to_pipe \
   --flow_file_prefix $EDR_FLOW_PREFIX --http_file_prefix $EDR_HTTP_PREFIX \
   --flow_record_count ${EDR_FLOW_COUNT:=200} --http_record_count ${EDR_HTTP_COUNT:=100} \
   --trickle_secs ${EDR_TRICKLE_SECS:=2} \
   --interval_secs ${EDR_INTERVAL_SECS=20} \
   .



