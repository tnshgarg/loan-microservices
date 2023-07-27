aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 802027775118.dkr.ecr.ap-south-1.amazonaws.com
docker tag media-processing:latest 802027775118.dkr.ecr.ap-south-1.amazonaws.com/media-processing:latest
docker push 802027775118.dkr.ecr.ap-south-1.amazonaws.com/media-processing:latest