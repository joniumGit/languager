## Languager

[![codecov](https://codecov.io/github/joniumGit/languager/branch/master/graph/badge.svg)](https://codecov.io/github/joniumGit/languager)

#### ISO639 Language Service

This module identifies languages from ISO639-1 and ISO639-3 codes or ISO names and provides a convenient class to access
related attributes. It is also possible to lookup codes for languages based on their ISO names. However, the name based
lookup will be slower as all language names are compared in lowercase for that.

Basic flows:

- Code is 2 characters
    - Lookup long code
    - Lookup data
- Code is 3 characters
    - Lookup data
- Code is something else
    - Loop all language names to check for match
        - `input_language == language_name.lower()`
    - Lookup data

This means that that Name based lookup is _n_-times slower than the other two options. But this really should not make a
difference.

#### Data

The data is taken from [iso639-3.sil.org](https://iso639-3.sil.org/code_tables/download_tables)
and is stored in the [tables](./languages/tables) folder. Further releases will update these tables.

#### Code

The code in [generator.py](./languages/generator.py) generates a single python file that contains all lookup tables and
methods.

#### Language

- __code__: The ISO639-3 Code
- __short__: ISO639-1 Code if available
- __deprecated__: True if the definition is deprecated
- __macro__: True if this is in a macrolanguage gropup
- __parent__: The parent macrolanguage
- __macros__: Any languages belonging to this macrolanguage

#### Examples

Checking the macrolanguages for Chinese:

```python
from languager import get_language

lang = get_language('zho')
# lang = get_language('zh')
# lang = get_language('Chinese')
# lang = get_language('does not exist', default='zho')

for language in lang.macros:
    print(language)

# czo
# csp
# yue
# cnp
# cmn
# czh
# hak
# nan
# wuu
# cjy
# lzh
# gan
# mnp
# cpx
# hsn
# cdo
```
