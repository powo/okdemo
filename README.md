# Flask Demo App

Simple Python/Flask Web-Application listening on Port 8080 and just serving
a single Page with some Infos for Demo purpose.

* Simulate **boot-up**, during the first **8s** after startup it will respond with
  a 503 HTTP Status Code and some error message
* If following Env-Vars (`DB_HOST,DB_NAME,DB_USER,DB_PASS`) are set, 
  it connects to a **Postgres-Database**
  * creates a table (if not yet existing)
  * updates one row in this table where it increases a counter
  * shows the counter in HTML response
* consumes lot of CPU (endless loop) for 200ms to simulate some Load
  


# initial Deployment Walkthrough

## Create a new Project
```bash
$ oc new-project okdemo
$ export PROJECT=`oc project -q`
```

## Create App using python s2i Builder image and Sourcecode from Github
```bash
$ oc new-app python~https://github.com/powo/okdemo.git
```

```
--> Creating resources ...
    imagestream.image.openshift.io "okdemo" created
    buildconfig.build.openshift.io "okdemo" created
    deploymentconfig.apps.openshift.io "okdemo" created
    service "okdemo" created
```

## Create a Route
```bash
$ oc create route edge --service=okdemo
export URL="https://"`oc get route okdemo -ogo-template='{{.spec.host}}'`
```
Test it (leaving it running in a loop):
```bash
$ while [ true ]; do curl -s $URL |head -1; sleep 1; done
```

## Add a Database (using template from OpenShift Service Catalog)
```bash
oc new-app postgresql-persistent \
        --name=demodb \
        -p DATABASE_SERVICE_NAME=demodb \
        -p VOLUME_CAPACITY=2Gi
```

```
--> Creating resources ...
    secret "demodb" created
    service "demodb" created
    persistentvolumeclaim "demodb" created
    deploymentconfig.apps.openshift.io "demodb" created
```


## Have a Look into ENV-Vars of our App Deployment "okdemo"
```bash
$ oc rsh dc/okdemo
sh-4.2$ printenv |grep DB_
```
... we do **not** yet have our `DB_HOST,DB_NAME,DB_USER,DB_PASS` Env vars, our 
App expects


## populate Env-Vars from demodb secret
```bash
oc edit dc/okdemo
``` 
add: (in `.spec.containers.env`):
```yaml
        env:
        - name: DB_HOST
          value: demodb
        - name: DB_NAME
          valueFrom:
            secretKeyRef:
              name: demodb
              key: database-name
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: demodb
              key: database-user
        - name: DB_PASS
          valueFrom:
            secretKeyRef:
              name: demodb
              key: database-password
```
... no hardcoded credentials here, just reference to secret




# Operational Tests

* leave the curl loop from above running in a separate window 

## Readyness Probe

* scale up `okdemo` Pod
  * when new Pod starts up (but app is not ready yet) => **outages**
  * ... because our App simulates a 503 response during first 8s after startup
* **Solution**: add a Readyness Probe (WebConsole or `oc edit dc/okdemo`)
  * now the Pod will not receive new requests until ready
  
## Deploy new version of App(Code)

* make change and push to git repo
* rebuild the App-image:
  ```bash
  $ oc start-build okdemo
  ```
  * finished build will automatically trigger Deployment
  
## Attach a temporary Container to a PVC

e.g. for reviewing/changing files on an existing persistent Volume
(`myvol` in this example, everything else should be left as-is)


```bash
oc run -i -t mypod --image=notused --restart=Never --rm=true --overrides='
{
        "apiVersion": "v1",
        "spec": {
            "containers": [
                {
                    "command": ["/bin/sh", "-i"],
                    "image": "busybox",
                    "stdin": true,
                    "tty": true,
                    "name": "mypod",
                    "volumeMounts": [{
                        "mountPath": "/mnt",
                        "name": "datavol"
                    }]
                }
            ],        
            "volumes": [
                {
                    "name": "datavol",
                    "persistentVolumeClaim": {
                        "claimName": "myvol"
                    }
                }
            ]
        }
}'  
```



# Next ?

## save all artifacts for later reuse
```bash
$ oc get all -l app=okdemo
oc get --export {is,bc,dc,service,route}/okdemo -o yaml > okdemo-all.yaml
```
(this is without the DB)

