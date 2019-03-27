# Walkthrough

## Create App using python s2i Builder image and Sourcecode from Github
```
$ oc new-app python~https://github.com/powo/okdemo.git
```

```
--> Creating resources ...
    imagestream.image.openshift.io "okdemo" created
    buildconfig.build.openshift.io "okdemo" created
    deploymentconfig.apps.openshift.io "okdemo" created
    service "okdemo" created
```