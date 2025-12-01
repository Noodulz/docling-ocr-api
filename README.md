# docling-ocr-api
Docling as a microservice to convert from PDF to markdown text.

## Pre-requisites
Docker, Python >= 3.11, MacOS/Linux terminal

## How to Run Locally
 1. Clone this repo and build the image with `docker build -t docling-ocr:latest .`
 2. Docker run with `docker run -p 8080:8080 docling-ocr:latest`
 3. Pass the PDF file name into curl request `curl -X POST -F "file=@{name_of_file}.pdf" http://localhost:8080/ocr`
