FROM andreasmalling/flixtube_init

WORKDIR /usr/src/app
COPY requirements.txt ./
COPY . .

# Install Splinter etc.
RUN pip3 install --no-cache-dir -r requirements.txt

# Add bin folder to path
ENV PATH="/usr/src/app/bin:${PATH}"

ENTRYPOINT [ "python3" ]

CMD [ "./emulated_user.py" ]