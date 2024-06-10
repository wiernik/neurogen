
CHUNK_SIZE=50
ITS_PATH=/gpfsscratch/rech/xdz/uow84uh/DATA/neurogen/L3_HIPAA_LENA_cleaned/its
WAV_PATH=/gpfsscratch/rech/xdz/uow84uh/DATA/neurogen/L3_HIPAA_LENA_cleaned/wav

NB_FILES=$(ls $ITS_PATH/*.its | wc -l)

i=0
DONE=0
j=0
while [[ $i -le $NB_FILES && $DONE == 0 ]]; do
  START=$i
  END=$(($i + $CHUNK_SIZE))
  if [[ $END -gt $NB_FILES ]]; then
    END=$NB_FILES
    DONE=1
  fi;
#  echo "ITS from $START to $END"
#  FILES_TO_COMPRESS=$(ls -1a $ITS_PATH/*.its | awk -v start=$START -v end=$END ' NR > start && NR <= end ')
#  printf "$FILES_TO_COMPRESS\n" > $ITS_PATH/chunk${j}.txt
#  zip -j $ITS_PATH/chunk${j} -@ < $ITS_PATH/chunk${j}.txt

  echo "WAV from $START to $END"
  FILES_TO_COMPRESS=$(ls -1a $WAV_PATH/*.wav | awk -v start=$START -v end=$END ' NR > start && NR <= end ')
  printf "$FILES_TO_COMPRESS\n" > $WAV_PATH/chunk${j}.txt
  zip -j $WAV_PATH/chunk${j} -@ < $WAV_PATH/chunk${j}.txt
  i=$END
  ((j++))
done;