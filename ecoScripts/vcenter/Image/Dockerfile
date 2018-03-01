FROM centos:centos7.4.1708
LABEL Project=ecoHub Name=Tetration-vCenter Version=0.1
WORKDIR /app
ADD . /app/

# add PowerShell
# https://github.com/PowerShell/PowerShell/blob/master/docs/installation/linux.md#centos-7
RUN curl https://packages.microsoft.com/config/rhel/7/prod.repo | tee /etc/yum.repos.d/microsoft.repo
RUN yum install -y powershell

# install VMware PowerCLI **BETA**
RUN pwsh 'Install-PowerCLI.ps1'

# install pip and then install dependencies
RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
RUN python get-pip.py
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# remove unneeded files
RUN rm -f requirements.txt
RUN rm -f get-pip.py

# run the app when the container launches
# ENTRYPOINT [ "/bin/bash" ]
ENTRYPOINT [ "python", "eco_action.py" ]