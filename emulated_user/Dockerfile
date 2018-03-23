FROM andreasmalling/flixtube_init

WORKDIR /usr/src/app
COPY bin/ ./bin/
COPY requirements.txt ./
COPY entrypoint.py .

# Install Splinter etc.
RUN pip3 install --no-cache-dir -r requirements.txt

# Add bin folder to path
ENV PATH="/usr/src/app/bin:${PATH}"

ENTRYPOINT [ "python3", "./entrypoint.py" ]