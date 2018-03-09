FROM mongo:3.6.3-jessie

WORKDIR /usr/src/app

RUN sudo apt-get update && sudo apt-get install -y 	\
	nodejs
	npm

COPY . .

RUN npm install
