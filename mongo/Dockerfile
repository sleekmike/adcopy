# AI Ad Copy Generator - MongoDB Dockerfile for Fly.io
FROM mongo:6.0

# Expose MongoDB's default port
EXPOSE 27017

# MongoDB will write its data files into /data/db by default.  
# We mount the Fly volume there for persistence:
VOLUME /data/db

# Use quiet mode to reduce verbose logging
# The base image already has a CMD to start mongod, but we override for our needs
CMD ["mongod", "--quiet", "--bind_ip_all"]
