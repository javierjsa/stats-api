FROM ubuntu:20.04

RUN apt-get update && apt install -y --no-install-recommends apt-utils python3-venv python3-pip && apt clean

# Copy code from project folder
COPY requirements.txt /root/statsapi/requirements.txt
COPY ./statsapi /root/statsapi/statsapi
COPY ./resources/11.parquet /root/statsapi/resources/11.parquet

# Activate virtualenv (https://pythonspeed.com/articles/activate-virtualenv-dockerfile/)
ENV VIRTUAL_ENV=/root/python-environments/fastapi-env
RUN mkdir /root/python-environments && python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install deps
RUN pip install --no-cache-dir -r /root/statsapi/requirements.txt

# Run app
ENV PYTHONPATH=/root/statsapi
WORKDIR /root/statsapi/statsapi
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
