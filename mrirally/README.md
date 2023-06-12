# A custom benchmark for MRI-like mock data

## Example document

```
{
  "ismrmrdHeader": "dwkFKtMMqL0lw30f283zucLYjxCiIlGTj7igSWuPX450t lcG72fOAIFDWomIcthusdUPWfYn881pu3lJy",
  "cflHeader": "9QD2O5RASmgnQF4FEVDmoA7BIrN6nuc9T2pdfcDRerw0hQaHs9fnryqRtzwbifcqEWSJLGYt0e0tITSzdl3mQn",
  "DataFormat": "nii.gz",
  "FrameOfReferenceUID": "DUgwJ4OnY1EJ1rZPImXwtEt9WdsQ6GWyKpeW",
  "MeasurementID": "51635707441",
  "StudyID": "58776",
  "StudyTimeText": "Oauei8dsCUVG",
  "SystemVendor": "GE",
  "SystemModel": "SIGNA",
  "ProtocolName": "GE2",
  "SystemFieldStrength": 7,
  "NumberReceiverChannels": 32,
  "InstitutionName": "University Hospital Tübingen",
  "InstitutionAddress": "T",
  "Trajectory": "Radial",
  "AcquisitionType": "2D",
  "AccelerationFactor": 1,
  "TR": 0.02,
  "TI": 0.2,
  "TE": 0.002,
  "FlipAngle": 79.0573,
  "SequenceType": "GradientEcho",
  "EchoSpacing": 0.001,
  "KspaceX": 64,
  "KspaceFOVX": 0.3575,
  "KspaceFOVY": 0.2588,
  "KspaceFOVZ": 0.3392,
  "KspaceReadout": 64,
  "KspacePhaseEnc1": 213,
  "KspacePhaseEnc2": 1,
  "KspaceCoils": 32,
  "KspaceMaps": 1,
  "KspaceTE": 1,
  "KspaceCoeff": 1,
  "KspaceCoeff2": 1,
  "KspaceIter": 1,
  "KspaceCshift": 1,
  "KspaceTime": 1,
  "KspaceTime2": 1,
  "KspaceLevel": 1,
  "KspaceSlice": 120,
  "KspaceAvg": 1,
  "ImageFOVX": 0.3575,
  "ImageFOVY": 0.2588,
  "ImageFOVZ": 0.3392,
  "ImageMatrixX": 64,
  "BaseResolution": 0,
  "ImageMatrixY": 1,
  "ImageMatrixZ": 39,
  "SliceThickness": 0.002,
  "BodyPart": "Knee",
  "PatientID": "1000001041",
  "PatientName": "Schmidt",
  "PatientBirthday": "1920-06-17",
  "PatientWeight": 88.8302,
  "PatientSex": "M",
  "PatientAge": 69,
  "StudyDate": "2011-11-27",
  "Lamor_frequency": 294,
  "TNumber": "T45920",
  "Tags": [
    "Tag8",
    "Tag7",
    "Tag6",
    "Tag1",
    "Tag2"
  ],
  "Filename": "2011-11-27_51635707441nii.gz",
  "BrainAge": 76
}
```

## How to generate the data

`./generate_json.sh` (just open it, very easy to read)

## How would this data be used?

See the queries defined in `track.json`, also once the paper is out it should be linked here

## Development 

See <https://esrally.readthedocs.io/en/stable/adding_tracks.html>

Playground container:
```
docker run --rm -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=false" elasticsearch:8.7.1
```

For development I recommend to use the `--test-mode` that only uses the first 1k entries of the corpus.

For scaling, generate a BIG corupus and use the `--track-params="ingest_percentage:X"` paramter

Note that the encrypted queries in the `track.json` assume that the OPE/AES Key/IV does not get changed.
