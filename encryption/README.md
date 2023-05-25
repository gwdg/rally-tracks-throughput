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
            "type": "date",
            "format": "YYYY-mm-dd"
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

**KeyType** `date` will simply be mapped by mapping `YYYY-mm-dd` to `YYYYmmdd` as a number. This will then get encrypted as an `int` using the input range `(0, 30000000)`.
In this case, we chose to use a more readable, easy-to-understand algorithm over the canonical unix-timpstamp alike solution of counting the days starting at any specific date.

**KeyType** `float` is more difficult.

First, we require that the triple `(min_range, max_range, step)` properly divides the interval `(min_range, max_range)`, i.e. the step size fits.
We know that `start + n * step = end`. Thus we require that `n = (end-start)/step` is a integer.

Now, given our input float `x`, we can map it on the interval `(start, end)` using the formula
`x = start + m * step`, i.e. `m = (x-start)/step`. This `m` can then be used for integer OPE on the input interval `(min_range, max_range)`.

The `step` can be seen as a descriptor on how granular the data has to be saved. If `x` does not fit on the grid, we map it to the nearest value. This is obviously a loss of precision; but one has to choose the trade off between number size and precision themselves. Therefore we assume that this trade off is made explicitly.

On first sight, this algorithm may seem unncessary complex. After speaking with some colleagues, the canonical solution seems to be along the lines of how the scientific notation works: Define an `e` so that `f_e(x) = int(x * 10^e)`.
But this solution is way inferior. Especially while working with SI units mapping over each small 1e-6 increment results in way too large numbers. Especially, if we also know that for example we only have the last digit ending with `0` or `5`. You get the idea.


## 3. Steps in applying this decryption to the rally benchmarks

1. Define a `index_encrypted.json` for the benchmark
2. Encrypt the corpus given the encryption methods defined in the `index_encrypted.json`
3. Change the size of the resulting corpus file in the `track.json`; feel free to encrypt it afterwards.
3. Change the attribute names in the `index.json` defining the elasticsearch index structure
4. Change all queries in the `operations` and `challenges` of the track to the new key and value names
