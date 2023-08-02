aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 802027775118.dkr.ecr.ap-south-1.amazonaws.com
docker tag kyc-service:latest 802027775118.dkr.ecr.ap-south-1.amazonaws.com/kyc-service:latest
docker push 802027775118.dkr.ecr.ap-south-1.amazonaws.com/kyc-service:latest