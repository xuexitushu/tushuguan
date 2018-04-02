#run_data_service.sh
sudo docker stop digits_data
sudo docker rm -f digits_data
sudo nvidia-docker run -it -d --name digits_data -v /home/yildirim/:/share -v /home/yildirim/data/workflow_manager/data:/workspace/jobs -p 5001:5000 nvcr.io/nvidia/digits:17.12
sleep 5
curl -c digits.cookie -XPOST 'http://127.0.0.1:5001/login' -F username=mobilityai


