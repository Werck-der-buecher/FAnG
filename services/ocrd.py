from typing import Union
from pathlib import Path
from collections import defaultdict
from typing import Union, List, Dict, Optional, Tuple, Any, Awaitable

import docker
import logging
import asyncio
import shutil
import re
import os


class OCRDService(object):

    @staticmethod
    def config_import_workspace(auto_convert: bool,
                                num_ids: bool,
                                dpi: int,
                                docker_image: str,
                                volumes: Optional[List[str]] = None,
                                working_dir: Optional[Union[str, Path]] = None,
                                environment_variables: Optional[List[str]] = None) -> Dict[str, Any]:
        cfg = {
            "name": 'ocrd_workflow_import',
            "Cmd": ["/bin/sh", "-c",
                    f"ocrd-import -i {'' if num_ids else '-P'} {'' if auto_convert else '-C'} -r {dpi} ./"],
            "Image": docker_image,
            "AttachStdin": True,
            "AttachStdout": True,
            "AttachStderr": True,
            "Tty": False,
            "OpenStdin": True,
            "StdinOnce": True}

        if volumes is not None:
            cfg['HostConfig'] = {"Binds": volumes}
        if working_dir is not None:
            cfg['WorkingDir'] = working_dir
        if environment_variables is not None:
            cfg['Env'] = environment_variables

        return cfg

    @staticmethod
    def config_exec_workflow(workflow_config: str,
                             docker_image: str,
                             docker_container_name: str = "ocrd_workflow_exec",
                             volumes: Optional[List[str]] = None,
                             working_dir: Optional[Union[str, Path]] = None,
                             environment_variables: Optional[List[str]] = None,
                             request_gpu: bool = True) -> Dict[str, Any]:
        cfg = {
            "name": docker_container_name,
            "Cmd": ["/bin/sh", "-c",
                    f"ocrd-make -f {workflow_config} ./"],
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

    async def split_workspaces_batch_size(self, data_dir: Union[str, Path], batch_size: int):
        """ Search for image files under the directory recursively and create a new workspace (if not already exists).
        :param data_dir:
        :param batch_size:
        :return:
        """

        def divide_chunks(l, n):
            # looping till length l
            for i in range(0, len(l), n):
                yield l[i:i + n]

        data_types = {'png': ('*.png', 'image/png'),
                      'jpeg': ('*.jpeg', 'image/jpeg'),
                      'jpg': ('*.jpg', 'image/jpeg'),
                      'tiff': ('*.tif', 'image/tiff')}

        files_grabbed = []
        for t in data_types.values():
            files_grabbed.extend(Path(data_dir).rglob(t[0]))

        workspaces: list[str] = []
        for batch_idx, batch_files in enumerate(divide_chunks(files_grabbed, batch_size)):
            if len(batch_files) == 0:
                continue

            wdir = Path(data_dir).joinpath(f"OCR-D_batch_{batch_idx}")
            if not wdir.exists():
                wdir.mkdir()

                # 1) Create symlinks to the data as relative paths to parent directories in METS files are not allowed.
                batch_symlinks = []
                for fn in batch_files:
                    dest_dir = wdir.joinpath("OCR-D-IMG")
                    dest_dir.mkdir(exist_ok=True)
                    sl = dest_dir.joinpath(fn.name)
                    # rel_sl = Path(f"../../{fn.name}")
                    rel_sl = os.path.relpath(fn, sl.parent)
                    sl.symlink_to(rel_sl)
                    # alterantive 'os.symlink(fn, sl)', both require priviliged mode/developed mode.
                    batch_symlinks.append(sl)
            else:
                logging.info("Workspace already exists! No action will be taken.")
            workspaces.append(str(wdir))

        return workspaces
