#run_training_service.sh
sudo docker stop digits
sudo docker rm -f digits
sudo nvidia-docker run -it -d --name digits -v /home/yildirim/:/share -v /home/yildirim/data/workflow_manager/cache:/workspace/jobs -p 5000:5000 mobility_ai:digits
sleep 5
curl -c digits.cookie -XPOST 'http://127.0.0.1:5000/login' -F username=mobilityai


