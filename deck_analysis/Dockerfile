# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM ubuntu

# Allow statements and log messages to immediately appear in the Knative logs

RUN apt update
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN apt install vim -y
RUN apt install --no-install-recommends\
    texlive-latex-base texlive-latex-extra -y

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

# Install production dependencies.
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# RUN pdflatex -output-directory=decks decks/decks.tex

# Fetching data
# WORKDIR $APP_HOME/data_ingestion
# RUN python cards_importer.py
# RUN python packs_importer.py
# WORKDIR $APP_HOME

# Run the web service on container startup.
# CMD panel serve src/app/cards_collection_viz.py --address 0.0.0.0 --port 5006 --allow-websocket-origin="*"