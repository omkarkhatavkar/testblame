#! /bin/bash

echo "export SENDGRID_API_KEY='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'" > sendgrid.env
echo "sendgrid.env" >> .gitignore
source ./sendgrid.env
pip install --editable .
echo "Test Blame Installed Successfully!"
