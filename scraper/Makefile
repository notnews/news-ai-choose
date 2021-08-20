latest:
	docker login -u AWS -p "$(shell aws ecr get-login-password --region us-east-2 --profile fourthbrain)" 681261969843.dkr.ecr.us-east-2.amazonaws.com

	docker build . --tag news-you-choose:latest

	docker tag news-you-choose:latest 681261969843.dkr.ecr.us-east-2.amazonaws.com/news-you-choose:latest

	docker push 681261969843.dkr.ecr.us-east-2.amazonaws.com/news-you-choose:latest
