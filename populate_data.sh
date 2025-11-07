#!/bin/bash

# Create data directory if it doesn't exist
mkdir -p data

# Download the dataset
echo "Downloading trainingandtestdata.zip..."
curl -o trainingandtestdata.zip http://cs.stanford.edu/people/alecmgo/trainingandtestdata.zip

# Unzip the file
echo "Unzipping the dataset..."
unzip trainingandtestdata.zip

# Move the required CSV file to the data directory
echo "Moving training.1600000.processed.noemoticon.csv to data/..."
mv training.1600000.processed.noemoticon.csv data/

# Clean up
echo "Cleaning up..."
rm trainingandtestdata.zip testdata.manual.2009.06.14.csv