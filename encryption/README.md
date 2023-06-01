# Rally data encryption

## 1. The Index definition
For each corpus, we definitely need a `index_encrypted.json`
This is designed analagously to the `index.json` in the rally benchmarks it should have the following format:
```
{
    "settings": {
        "OPE": {
            "key": "cJ2x4CY+e9+Egi29p0Db9b4iz3woTnTHaX9OX7BRdWc="
        },
        "AES": {
            "key": "SOME 32 BYTES",
            "iv": "SOME 16 BYTES"
        },
        "ENCRYPT_KEYS": true /* default: true */
    },
    "attributes": {
        "some_text": {
            "type": "str"
        },
        "some_keyword": {
            "type": "str"
        },
        "some_integer": {
            "type": "int"
            "min_range": 0,
            "max_range" 2048
        },
        "some_float": {
            "type": "float"
            "min_range": 0.02,
            "max_range": 10.0,
            "step": 0.02
        },
        "some_date": {
            "type": "date"
        },
        "array_allowed": {
            "type": "str",
            "multi": true
        }
    }
}
```

## 2. The encryption

Here we will cover how the index gets encrypted. We encrypt each attribute given its beforementioned JSON definition.

**Keys** will get encrypted using AES256 and the Key/IV provided by the `index_encrypted.json`. 
The output bytes will get decoded as Hex using `binascii.hexlify`.

**KeyType** `str` will get encrypted using AES256 and the Key/IV provided by the `index_encrypted.json`.
The output bytes will get decoded as Hex using `binascii.hexlify`.

**KeyType** `int` will be encrypted using OPE and the Key provided by the `index_encrypted.json`.
The input range will be `(min_range, max_range)`.
The output range is fixed to `(0, 2^32-1)`.

**KeyType** `date` will simply be mapped by mapping `YYYY-mm-dd` to `YYYYmmdd` as a number. This will then get encrypted as an `int` using the input range `(0, 30000000)`. For now, other formats than "YYYY-mm-dd" are not supported.

**KeyType** `float` is more difficult.

First, we require that the triple `(min_range, max_range, step)` properly divides the interval `(min_range, max_range)`, i.e. the step size fits.
We know that `start + n * step = end`. Thus we require that `n = (end-start)/step` is a integer.

Now, given our input float `x`, we can map it on the interval `(start, end)` using the formula
`x = start + m * step`, i.e. `m = (x-start)/step`. This `m` can then be used for integer OPE on the input interval `(min_range, max_range)`.

The `step` can be seen as a descriptor on how granular the data has to be saved. If `x` does not fit on the grid, we truncate it to the value below. This is obviously a loss of precision; but one has to choose the trade off between number size and precision themselves. Therefore we assume that this trade off is made explicitly.

On first sight, this algorithm may seem unncessary complex. After speaking with some colleagues, the canonical solution seems to be along the lines of how the scientific notation works: Define an `e` so that `f_e(x) = int(x * 10^e)`.
But this solution is way inferior. Especially while working with SI units mapping over each small 1e-6 increment results in way too large numbers. Especially, if we also know that for example we only have the last digit ending with `0` or `5`. You get the idea.


## 3. Steps in applying this decryption to the rally benchmarks

1. Define a `index_encrypted.json` for the benchmark
2. Encrypt the corpus given the encryption methods defined in the `index_encrypted.json`. This is done via the `main.py` script.
3. Change the size of the resulting corpus file in the `track.json`; feel free to encrypt it afterwards.
3. Change the attribute names in the `index.json` defining the elasticsearch index structure. See `4.` on how to do it.
4. Change all queries in the `operations` and `challenges` of the track to the new key and value names. See `4.` on how to do it.

## 4. How to encrypt any kind of data

It would be overkill to create extra scripts to encrypt the operations or index, as this is such a small amount of data that it can be done within a few minutes of manual work.

Let me explain how to do it.

Lets say you want to encrypt the following query
```
"query": {
  "bool": {
    "must": [
      {
        "term": {
          "foo": "bar"
        }
      },
      {
        "range": {
          "baz": {
            "gte": 42,
            "lt": 1337
          }
        }
      }
    ]
  }
}
```

Then, you would create the following JSON file (wlog `query.json` here)
```
{"foo": "bar"}
{"baz": 42}
{"baz": 1337}
```
Now you can encrypt it using `main.py` and the same `index_encrypted.json` used for the corpus data file. Afterwards, it will look along the lines of
```
{"a06afa2d7b35": "72482bacffe"}
{"042b0e2c3af1": 11499}
{"042b0e2c3af1": 438l7}
```
Since the line ordering doesnt change, one can easily deduce in which line corresponds to which unencrypted key value pair.

This way, one can manually patch the files mentioned.
