rm academics.zip
zip -vr academics academics -i '*.py'
zip -u academics.zip lambda_function.py
cd packages
zip -r9 ../academics.zip .
cd ..
aws lambda update-function-code --function-name academic-integrator --zip-file fileb://academics.zip
aws s3 cp academics.zip s3://gc-lambda-deploy/academic-integrator/academics.zip
