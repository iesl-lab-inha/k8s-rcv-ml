echo `kubectl delete -f rcvserver.yaml`
echo `kubectl delete deploy image-deploy -n default`
echo `kubectl delete deploy scalar-deploy -n default`

