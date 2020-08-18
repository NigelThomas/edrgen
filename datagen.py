# datagen.py
# Derived from the original java / python / bash
#
# - Generates flow and http data files based on model data in two sample files
# - Handles typical CSV data (quoted, comma separated) 
# - Writes data to CSV files (minimally quoted)
# - supports writing to a named pipe for each file type (FLOW, EDR) so that we can pipe 
#   data into helper tools like zcat, kafkacat, etc

import random
import string
import argparse
import logging
import time
import csv

logger = logging.getLogger('datagen')
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

# File name masks
flowFilePrefix="SPGWPH5_wap_adult-flow-edr_"
httpFilePrefix="SPGWPH5_wap_adult-http-edr_"
fileSuffix="_001_000005502"

# FTIME format is 06072020101036 = ddMMyyyyHHmmss (or coukd be MMdd?)

# to replace bash / java / python with a single python script

# could instead use random longint and convert to IP
def getRandomIPAdd():
    return str(random.randint(0,256)) + '.' + \
        str(random.randint(0,256)) + '.' + \
        str(random.randint(0,256)) + '.' + \
        str(random.randint(0,256))

# return random as a string
def getRandomNumberInRange(min, max):
    return str(random.randint(min,max))



def read_model_file(filename, recs_to_read):
    rows = []
    with open(filename, mode="r", encoding="latin1") as f:
        csvreader = csv.reader(f,delimiter=",", quotechar='"')
        for i in range(0, recs_to_read):
            row = next(csvreader)
            rows.append(row)
    return rows

def get_filename(file_prefix, epoch_time, file_suffix):
    if args.write_to_pipe:
        return file_prefix
    else:
        return file_prefix + "_" + time.strftime("%d%m%Y%H%M%S", time.localtime(epoch_time)) + "_" + file_suffix

def emit_batch(rectype, file_prefix, file_suffix, batch_start_time, model_rows, recs_available, field_count):

    filename = get_filename(file_prefix, batch_start_time, file_suffix)
    batch_end_time = batch_start_time + args.interval_secs
    logger.info("emit "+rectype+" batch at "+str(batch_start_time)+ " to "+filename)

    # write as append in case writing to a pipe

    with open(args.tempdir+"/"+filename, 'a') as outfile:
        csvwriter = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)

        for i in range(0,recs_available):
            oldrow = []
            while len(oldrow) != field_count:
                # make sure to skip bad rows
                # generate a line
                rx = random.randint(0,recs_available)
                logger.debug("generating "+rectype+" line "+str(i)+" using model line "+str(rx))
                oldrow = model_rows[rx]

            newrow = [ str(batch_start_time)
                        , str(batch_end_time)
                        , getRandomNumberInRange(1000000000,1005000000)
                        , getRandomIPAdd()
                        , oldrow[4]
                        , getRandomIPAdd()
                        , oldrow[6]
                        , getRandomIPAdd()
                        ]   + oldrow[8:19] + oldrow [21:]

            newline = ",".join(newrow)

            # write the data out
            logger.debug(rectype+":"+newline)
            csvwriter.writerow(newrow)

        outfile.close()

flow_model_file = 'SPGWPH5_wap_adult-flow-edr'
http_model_file = 'SPGWPH5_wap_adult-http-edr'

parser = argparse.ArgumentParser()
# default start = 1 Aug 2020 at 00:00
parser.add_argument("-s","--start_time",type=int, default=1596240000, help="start time epoch millis")
# default end = 1 Aug 2020 at 00:30
parser.add_argument("-e","--end_time",type=int, default=1596241800, help="end time epoch millis")
parser.add_argument("-i","--interval_secs",type=int, default=20, help="time interval between batches")
parser.add_argument("-t","--trickle_secs",type=int, default=2, help="Seconds to sleep between batches")
parser.add_argument("-f","--flow_record_count", type=int, default=200, help="Flow records in batch")
parser.add_argument("-H","--http_record_count", type=int, default=100, help="HTTP records in batch")
parser.add_argument("--flow_file_prefix", default=flow_model_file, help="Flow file prefix")
parser.add_argument("--http_file_prefix", default=http_model_file, help="HTTP file prefix")
parser.add_argument("--file_suffix", default="001_000005502", help="Shared file suffix")
parser.add_argument("-p","--write_to_pipe", default=False, action='store_true', help="Write to a pipe")
parser.add_argument('tempdir', metavar='temp_directory', help="Location for output files")

args = parser.parse_args()
# addsec=$1
# intime=$2
# starttime=$2
# recordshttp=$3
# recordsflow=$4

# Read from the model files

flow_model_lines = read_model_file(flow_model_file, args.flow_record_count)
http_model_lines = read_model_file(http_model_file, args.http_record_count)

# now process the data

for batch_start_time in range(args.start_time, args.end_time+1, args.interval_secs):

    if args.trickle_secs > 0 and batch_start_time > args.start_time:
        logger.debug("sleeping for "+str(args.trickle_secs))
        time.sleep(args.trickle_secs)

    emit_batch("FLOW", args.flow_file_prefix, args.file_suffix, batch_start_time, flow_model_lines, args.flow_record_count-1, 29)
    emit_batch("HTTP", args.http_file_prefix, args.file_suffix, batch_start_time, http_model_lines, args.http_record_count-1, 30)



