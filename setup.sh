#! /bin/bash

if [[ -z "$1" ]]
  then
    echo -e "\e[31mPlease Pass SendGrid API Key as argument to use Email Functionality \e[0m"
else
    echo "export SENDGRID_API_KEY='$1'" > sendgrid.env
    echo "sendgrid.env" >> .gitignore
    source ./sendgrid.env
fi

pip install --editable .
echo -e "\e[92mTest Blame Installed Successfully!\e[0m"
