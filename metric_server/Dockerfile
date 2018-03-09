FROM node:9.8.0

WORKDIR /usr/src/app

COPY . .

RUN npm install

ENTRYPOINT [ "node" ]

CMD [ "./metric_server.js" ]


