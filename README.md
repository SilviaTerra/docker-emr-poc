# docker-emr-poc

### Installation (OSX)
```
mkdir ~/docker-mnt

# install Docker through brew and create a default machine
brew install docker
brew install docker-machine
docker-machine create --driver virtualbox default

# pull docker image
docker pull silviaterra/emr-poc

# install python deps
pip install -r requirements/base.txt
pip-sync requirements/base.txt
```

## Running a mapreduce job on EMR
```
echo bilbo | python mr_demo.py -r emr \
    --ec2-master-instance-type m3.xlarge \
    --num-ec2-core-instances 1 \
    --ec2-core-instance-type m3.xlarge
```

## Running a mapreduce job locally
```
echo bilbo | python mr_demo.py
```

## Using utils/docker.py
```
python -c "from utils import docker; print docker.run_my_cmd(['python', '/opt/docker-emr-poc/demo.py', 'Bilbo'])"
# Returns: {u'status': u'OK', u'message': u'Howdy there Bilbo', u'a number': 5}
```

## Updating requirements
```
# update requirements/base.in
# ...

pip-compile requirements/base.in > requirements/base.txt
```

## Updating Docker Image
```
# make changes in Dockerfile
# ...

# Build new image
cd docker
docker build -t emr-poc .

# Get image id
docker images

# tag and push
docker tag <IMAGE ID> silviaterra/emr-poc:latest
```
