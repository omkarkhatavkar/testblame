#! /bin/bash

if [[ -z "$1" ]]
  then
    echo -e "\e[31mPlease Pass SendGrid API Key as argument to use Email Functionality \e[0m"

elif [ "$#" -eq 2 ]
  then
   echo "export SMTP_SERVER_NAME='$1'" > sendgrid.env
   echo "export SMTP_SERVER_PORT='$2'" >> sendgrid.env
   echo "sendgrid.env" >> .gitignore
   source ./sendgrid.env

else
    echo "export SENDGRID_API_KEY='$1'" > sendgrid.env
    echo "sendgrid.env" >> .gitignore
    source ./sendgrid.env
fi

pip install --editable .
echo -e "\e[92mTest Blame Installed Successfully!\e[0m"
