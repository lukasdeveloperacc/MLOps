from kfp import Client

import logging

import kfp_server_api

logging.basicConfig(level=logging.INFO)

class KFPClient:
    def __init__(self, host: str, **kwargs) -> None:
        self._client = Client(host=host, **kwargs)
        
    def get_experiment(self, experiment_id: str | None = None, experiment_name: str | None = None, namespace: str | None = None):
        try:
            experiment = self._client.get_experiment(experiment_id=experiment_id, experiment_name=experiment_name, namespace=namespace)
            return experiment
        except ValueError:
            return None

    def create_experiment(self, name: str, description: str | None = None, namespace: str | None = None):
        try:
            experiment = self.get_experiment(experiment_name=name, namespace=namespace)
            logging.info(f"Experiment {name} {experiment.experiment_id} already exists")
            
        except ValueError:
            logging.info(f"Experiment {name} not found")
            self._client.create_experiment(name, description=description, namespace=namespace)
            logging.info(f"Experiment {name} created")
    
    def delete_experiment(self, name: str, namespace: str | None = None):
        try:
            experiment = self.get_experiment(experiment_name=name, namespace=namespace)
            logging.info(f"Deleting experiment {experiment.experiment_id}")
            self._client.delete_experiment(experiment.experiment_id)
            logging.info(f"Experiment {experiment.experiment_id} deleted")
            
        except ValueError:
            logging.error(f"Experiment {name} not found")
            
    def get_pipeline_version_id(self, pipeline_name: str, version_name: str) -> str:
        pipeline_id = self._client.get_pipeline_id(pipeline_name)
        if pipeline_id is None:
            raise ValueError(f"Pipeline '{pipeline_name}' not found.")
        
        versions = self._client.list_pipeline_versions(pipeline_id=pipeline_id, sort_by="created_at desc").pipeline_versions
        
        for version in versions:
            if version.display_name == version_name:
                logging.info(f"Pipeline version {version_name} found")
                return version.pipeline_version_id
        
        raise ValueError(f"Pipeline version '{version_name}' not found.")
            
    def upload_pipeline_version(self, pipeline_package_path: str, pipeline_version_name: str, pipeline_name: str, description: str | None = None, retry: int = 1):
        try:
            if retry < 0:
                raise ValueError(f"Failed to upload pipeline {pipeline_name} {pipeline_version_name} after {retry+1} retries.")
            
            pipeline_id = self._client.get_pipeline_id(pipeline_name)
            if pipeline_id is None:
                raise ValueError(f"Pipeline '{pipeline_name}' not found.")
            else:
                logging.info(f"Pipeline {pipeline_name} found")
            
            self._client.upload_pipeline_version(pipeline_package_path, pipeline_version_name=pipeline_version_name, pipeline_name=pipeline_name, description=description)
            logging.info(f"Pipeline {pipeline_name} {pipeline_version_name} uploaded")
            
        except ValueError as e:
            logging.error(f"Failed to upload pipeline {pipeline_name} {pipeline_version_name}: {e}")
            
        except kfp_server_api.ApiException as e:
            logging.error(f"Failed to upload pipeline {pipeline_name} {pipeline_version_name}: {e}\nDeleting pipeline version...")
            pipeline_version_id = self.get_pipeline_version_id(pipeline_name=pipeline_name, version_name=pipeline_version_name)
            self._client.delete_pipeline_version(pipeline_id=pipeline_id, pipeline_version_id=pipeline_version_id)
            logging.info(f"Pipeline version {pipeline_version_name} deleted and retrying...")
            self.upload_pipeline_version(pipeline_package_path=pipeline_package_path, pipeline_version_name=pipeline_version_name, pipeline_name=pipeline_name, description=description, retry=retry-1)
            
    def delete_pipeline_version(self, pipeline_name: str, version_name: str):
        try:
            pipeline_id = self._client.get_pipeline_id(pipeline_name)
            if pipeline_id is None:
                raise ValueError(f"Pipeline '{pipeline_name}' not found.")
            
            pipeline_version_id = self.get_pipeline_version_id(pipeline_name=pipeline_name, version_name=version_name)
            self._client.delete_pipeline_version(pipeline_id=pipeline_id, pipeline_version_id=pipeline_version_id)
            logging.info(f"Pipeline version {version_name} deleted")
            
        except ValueError as e:
            logging.error(f"Failed to delete pipeline version {version_name}: {e}")
            
    def delete_pipeline(self, pipeline_name: str):
        try:
            pipeline_id = self._client.get_pipeline_id(pipeline_name)
            if pipeline_id is None:
                raise ValueError(f"Pipeline '{pipeline_name}' not found.")
            
            self._client.delete_pipeline(pipeline_id=pipeline_id)
            logging.info(f"Pipeline {pipeline_name} deleted")
            
        except ValueError as e:
            logging.error(f"Failed to delete pipeline {pipeline_name}: {e}")
            
            

if __name__ == "__main__":
    kfp_client = KFPClient("http://localhost:32531", namespace="kubeflow")
    kfp_client.upload_pipeline_version(pipeline_package_path="./unet/pipeline.yaml", pipeline_version_name="v1", pipeline_name="Unet")
