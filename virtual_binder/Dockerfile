# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM ubuntu

# Allow statements and log messages to immediately appear in the Knative logs

RUN apt update
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN apt install vim -y

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY virtual_binder ./
COPY data ./data

# Install production dependencies.
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run the web service on container startup.
CMD panel serve cards_collection_viz.py --address 0.0.0.0 --port 5006 --allow-websocket-origin="*"