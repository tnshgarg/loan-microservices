aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 802027775118.dkr.ecr.ap-south-1.amazonaws.com
docker tag jupyter_debug:latest 802027775118.dkr.ecr.ap-south-1.amazonaws.com/jupyter_debug:latest
docker push 802027775118.dkr.ecr.ap-south-1.amazonaws.com/jupyter_debug:latest


aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 802027775118.dkr.ecr.ap-south-1.amazonaws.com
docker tag jupyter_debug:latest 802027775118.dkr.ecr.ap-south-1.amazonaws.com/jupyter_debug:latest
docker push 802027775118.dkr.ecr.ap-south-1.amazonaws.com/jupyter_debug:latest