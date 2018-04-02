#restart_trainer.sh
echo "stopping digits"
sudo docker stop digits
sleep 10
echo "deleting cache"
sudo rm -rf /home/yildirim/data/workflow_manager/cache/*
echo "removing dbs"
rm /home/yildirim/playground/workflow_manager_dl/*.db
echo "starting digits"
sh  /home/yildirim/playground/workflow_manager_dl/scripts/run_training_service.sh
sudo python /home/yildirim/playground/workflow_manager_dl/__main__.py -c config_trainer.json



