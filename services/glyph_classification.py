from pathlib import Path
from typing import Union, List, Dict, Optional, Any


class GlyphClassifierService(object):
    def __init__(self, service_cfg):
        self.service_cfg = service_cfg

    def config_exec_workflow(self,
                             docker_image: str,
                             docker_container_name: str = 'glyph_classifier',
                             volumes: Optional[List[str]] = None,
                             working_dir: Optional[Union[str, Path]] = None,
                             environment_variables: Optional[List[str]] = None,
                             request_gpu: bool = True,
                             score_threshold: float = 0.5,
                             padding: int = 10) -> Dict[str, Any]:
        cfg = {
            "name": docker_container_name,
            "Cmd": ["/bin/sh", "-c",
                    "python /classifier/classify_glyphs.py "
                    "--input OCR-D-EXTGLYPHS-tesseract "
                    "--output OCR-D-EXTGLYPHS_pruned "
                    "--model_dir /models "
                    f"--score_threshold {score_threshold} "
                    "--device cuda:0 "
                    f"--img_padding {padding}"
                    ],
            "Image": docker_image,
            "AttachStdin": True,
            "AttachStdout": True,
            "AttachStderr": True,
            "Tty": False,
            "OpenStdin": True,
            "StdinOnce": True,
            "HostConfig": {}}

        if request_gpu:
            cfg['HostConfig']['DeviceRequests'] = [
                {
                    "Driver": "",
                    "Count": 0,
                    "DeviceIDs": [
                        "0"
                    ],
                    "Capabilities": [
                        [
                            "gpu"
                        ]
                    ],
                    "Options": {}
                }
            ]
        if volumes is not None:
            cfg['HostConfig']['Binds'] = volumes
        if working_dir is not None:
            cfg['WorkingDir'] = working_dir
        if environment_variables is not None:
            cfg['Env'] = environment_variables

        return cfg
