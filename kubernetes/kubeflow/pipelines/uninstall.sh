#/bin/sh

# Reference : https://www.kubeflow.org/docs/components/pipelines/operator-guides/installation/
export PIPELINE_VERSION=2.4.0
kubectl delete -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=${PIPELINE_VERSION}"
kubectl delete -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=${PIPELINE_VERSION}"
