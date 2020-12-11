#### USAGE ####

## IMPORT BASE IMAGE
oc import-image -n openshift ubi8-python-38:1-27 --from=registry.access.redhat.com/ubi8/python-38:1-27 --confirm
 
## VERIFYING IMAGESTREAM
helm template ./helm/build-is-redis/. --values ./helm/build-is-redis/values.yaml
 
## DRY RUN
helm upgrade build-is-redis ./helm/build-is-redis/. --values ./helm/build-is-redis/values.yaml \
--install --timeout 1800 --tiller-namespace redis-ops --wait --debug --dry-run
 
## INSTALLING IMAGESTREAM & BUIDLCONFIG
helm upgrade build-is-redis ./helm/build-is-redis/. --values ./helm/build-is-redis/values.yaml \
--install --timeout 1800 --tiller-namespace redis-ops --wait --debug
 
# helm upgrade <release name> <path to chart>
# --install, run install if release doesn't already exist
 
## BUILDING IMAGE
oc start-build redis-probe-builder --from-dir src/
 
## VERIFYING
helm template ./helm/redis-probe/. --values ./helm/redis-probe/values.yaml
 
## DRY RUN
helm upgrade redis-probe ./helm/redis-probe/. --values ./helm/redis-probe/values.yaml \
--install --timeout 1800 --tiller-namespace redis-ops --wait --debug --dry-run
 
## INSTALLING DEPLOYMENT
helm upgrade redis-probe ./helm/redis-probe/. --values ./helm/redis-probe/values.yaml \
--install --timeout 1800 --tiller-namespace redis-ops --wait --debug