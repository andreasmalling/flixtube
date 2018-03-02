FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# FIXME: Add bin (drivers) to path 
# (https://splinter.readthedocs.io/en/latest/drivers/chrome.html#linux-common-steps-for-32-and-64bits)

# CMD [ "python", "./splinter.py" ]
CMD [ "python", "./hello.py" ]
