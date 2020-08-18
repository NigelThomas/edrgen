
docker run -d --name edrgen --rm 
   -e EDR_START_EPOCH=${EDR_START_EPOCH:=`date +%s"`} \
   -e EDR_END_EPOCH=${EDR_END_EPOCH:=$(eval $EDR_START_EPOCH + 300)} \
   -e EDR_FLOW_COUNT=${EDR_FLOW_COUNT:=200} \
   -e EDR_HTTP_COUNT=${EDR_HTTP_COUNT:=100} \
   -e EDR_TRICKLE_SECS=${EDR_TRICKLE_SECS:=2} \
   -e EDR_INTERVAL_SECS=${EDR_INTERVAL_SECS:=20} \
   -e EDR_KAFKA_CONFIG=${EDR_KAFKA_CONFIG:=kafka.config} \
   sqlstream/edrgen
