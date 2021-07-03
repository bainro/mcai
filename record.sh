#!/bin/bash 

# duration to record experience tuples: (S, A, S', R)
export MC_DUR=600

python ./grab.py    second_zom_room $MC_DUR &
python ./actions.py second_zom_room $MC_DUR &
node   ./rewards.js second_zom_room $MC_DUR &

sleep $MC_DUR

echo "all done!"