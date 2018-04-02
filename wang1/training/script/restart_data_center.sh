#scripts/
#restart_data_center.sh
echo "stopping digits"
sudo docker stop digits_data
sleep 10
echo "deleting datacenter cache"
sudo rm -rf /home/yildirim/data/workflow_manager/data/*
echo "starting digits"
sh  /home/yildirim/playground/workflow_manager_dl/scripts/run_data_service.sh


