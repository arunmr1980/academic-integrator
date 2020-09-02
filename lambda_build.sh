rm academics.zip
zip -vr academics academics -i '*.py'
zip -u academics.zip lambda_function.py
aws lambda update-function-code --function-name academic-integrator --zip-file fileb://academics.zip
