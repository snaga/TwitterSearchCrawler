FUNCTION_NAME=twitter-search-crawler-dev

TARGET=twitter_search_crawler.zip

SRCS=lambda_function.py twitter_search_crawler.py local_to_dlk.py

all: $(TARGET)

$(TARGET): $(SRCS)
	zip -r $(TARGET) $(SRCS)

	pip install --target ./deps requests-oauthlib
	cd deps; zip -r ../$(TARGET) .; cd ..

install: $(TARGET)
	aws lambda update-function-code --function-name $(FUNCTION_NAME) --zip-file fileb://$(TARGET)
	aws lambda update-function-configuration --function-name $(FUNCTION_NAME)  --timeout 900 \
	    --environment "Variables={API_KEY=${API_KEY},API_KEY_SECRET=${API_KEY_SECRET},ACCESS_TOKEN=${ACCESS_TOKEN},ACCESS_TOKEN_SECRET=${ACCESS_TOKEN_SECRET},KEYWORD=${KEYWORD},YYYYMMDDHH=${YYYYMMDDHH},S3_AWS_ACCESS_KEY_ID=${S3_AWS_ACCESS_KEY_ID},S3_AWS_SECRET_ACCESS_KEY=${S3_AWS_SECRET_ACCESS_KEY},BUCKET_NAME=${BUCKET_NAME},OBJECT_KEY_PREFIX=${OBJECT_KEY_PREFIX}}"

clean:
	rm -rf *~ deps $(TARGET)
