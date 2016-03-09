# docker-emr-poc

## Running an example
```
python -c "from utils import docker; print docker.run_my_cmd(['python', '/opt/docker-emr-poc/demo.py', 'Bilbo'])"
# Returns: {u'status': u'OK', u'message': u'Howdy there Bilbo', u'a number': 5}
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
