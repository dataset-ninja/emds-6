Dataset **EMDS-6** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/remote/eyJsaW5rIjogImZzOi8vYXNzZXRzLzM1NTFfRW52aXJvbm1lbnRhbCBNaWNyb29yZ2FuaXNtIEltYWdlIERhdGFzZXQvZW52aXJvbm1lbnRhbC1taWNyb29yZ2FuaXNtLWltYWdlLWRhdGFzZXQtRGF0YXNldE5pbmphLnRhciIsICJzaWciOiAiWDl0VmNZOHJmU0c4ZTlrVllYYVZqYXRPcWFTUk81TXBCbHJ2N2tuUWp3az0ifQ==)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='EMDS-6', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be [downloaded here](https://figshare.com/ndownloader/files/31660352).