FROM selenium/standalone-chrome:3.9.1-actinium

RUN sudo apt-get update && sudo apt-get install -y 	\
	python3									\
	python3-pip

WORKDIR /usr/src/app
COPY bin/ ./bin/
COPY requirements.txt ./
COPY src/ ./src/

# Install Splinter etc.
RUN pip3 install --no-cache-dir -r requirements.txt

# Add bin folder to path
ENV PATH="/usr/src/app/bin:${PATH}"

ENTRYPOINT [ "python3", "./src/entrypoint.py" ]