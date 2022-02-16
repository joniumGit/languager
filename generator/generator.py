import csv
import re
import textwrap


def skip_one(iter_):
    next(iter_)
    return iter_


def read_csv(file: str, *columns: int):
    with open(file, 'r') as f:
        for row in skip_one(csv.reader(f, delimiter='\t')):
            if len(columns) == 1:
                yield row[columns[0]].strip()
            else:
                yield tuple(row[i].strip() for i in columns)


name_table = {id_.lower(): name for id_, name in read_csv('./tables/iso-639-3_Name_Index.tab', 0, 1)}
ref_table = {id_.lower(): part1.lower() for id_, part1 in read_csv('./tables/iso-639-3.tab', 0, 3) if part1 != ''}
macro_table = {macro.lower(): id_.lower() for id_, macro in read_csv('./tables/iso-639-3-macrolanguages.tab', 0, 1)}
retired_set = {id_.lower() for id_ in read_csv('./tables/iso-639-3_Retirements.tab', 0)}

names = ',\n'.join(f'    "{k}": "{v}"' for k, v in name_table.items())
stl = ',\n'.join(f'    "{v}": "{k}"' for k, v in ref_table.items())
lts = ',\n'.join(f'    "{k}": "{v}"' for k, v in ref_table.items())
dep = ',\n'.join(f'    "{v}"' for v in retired_set)


def macros(lang_id: str):
    return ",\n".join(map(lambda e: f'        "{e[0]}"', filter(lambda e: e[1] == lang_id, macro_table.items())))


mtp = ',\n'.join(f'    "{k}": "{v}"' for k, v in macro_table.items())
ptm = ',\n'.join(f'    "{k}": [\n{macros(k)}\n    ]' for k in ref_table.keys() if k in macro_table.values())

source = textwrap.dedent(
    """
    \"\"\"
    Generated File
    
    Do not modify directly.
    \"\"\"
    
    from dataclasses import dataclass, field
    from functools import lru_cache
    from typing import Optional, FrozenSet
    
    NAMES = {{
    {names}
    }}
    SHORT_TO_LONG = {{
    {stl}
    }}
    LONG_TO_SHORT = {{
    {lts}
    }}
    DEPRECATED = {{
    {dep}
    }}
    MACRO_TO_PARENT = {{
    {mtp}
    }}
    PARENT_TO_MACROS = {{
    {ptm}
    }}
    
    
    @dataclass(order=True, frozen=True)
    class Language:
        \"\"\"Represents a language
        
        Attributes
        ----------
        code
            ISO639-03 Language code
        short
            ISO639-01 Language code if available
        name
            ISO Standard Name for the language
        deprecated
            Indicates this code is deprecated
        macro
            If True, indicates this is a member of a macrolanguage group
        parent
            Parent for this macrolanguage group member
        macros
            Contains all children if this is a macrogroup parent
        \"\"\"
        code:           str             = field(compare=True,  hash=True)
        short:          Optional[str]   = field(compare=False, hash=False)
        name:           str             = field(compare=False, hash=False) 
        deprecated:     bool            = field(compare=False, hash=False)
        macro:          bool            = field(compare=False, hash=False)
        parent:         Optional[str]   = field(compare=False, hash=False)
        macros:         FrozenSet[str]  = field(compare=False, hash=False)
    
    
    def _get_language(language: str) -> Language:
        try:
            language = language.lower()
            if len(language) == 2:
                long_id = SHORT_TO_LONG[language]
                short_id = language
            elif len(language) == 3:
                short_id = LONG_TO_SHORT.get(language, None)
                long_id = language
            else:
                long_id = None
                for e in NAMES.items():
                    if e[1].lower() == language:
                        long_id = e[0]
                if long_id is None:
                    raise ValueError('Invalid Language Tag: Not Found')
                short_id = LONG_TO_SHORT.get(long_id, None)
            parent = MACRO_TO_PARENT.get(long_id, None)
            return Language(
                code=long_id,
                short=short_id,
                name=NAMES[long_id],
                parent=parent,
                macros=frozenset(PARENT_TO_MACROS.get(long_id, frozenset())),
                deprecated=long_id in DEPRECATED,
                macro=parent is not None
            )
        except KeyError:
            raise ValueError('Invalid Language Tag: Not Found')
    
    
    @lru_cache(maxsize=16, typed=False)
    def get_language(language: str, *, default: Optional[str] = None) -> Language:
        \"\"\"Looks up a language
        
        The language can be in one of the following formats:
        
        - ISO639-01 e.g. fi
        - ISO639-03 e.g. fin
        - ISO Name  e.g.  Finnish
        
        Parameters
        ----------
        language
            The language code or name to look up
        default: optional
            The language code or name to use if the language is not found
        
        Returns
        -------
        language
            Language instance for the looked up language
        
        Raises
        ------
        ValueError
            If the language lookup fails, format _Invalid Language Tag: reason_
        
        Examples
        ---------
        >>> get_language('nor')
        Language(code='nor', short='no', name='Norwegian', deprecated=False, macro=False, parent=None, macros=frozenset({{'nob', 'nno'}}))
    
        >>> get_language('Finnish')
        Language(code='fin', short='fi', name='Finnish', deprecated=False, macro=False, parent=None, macros=frozenset())
        
        Notes
        -----
        The lookup is case insensitive, so FI, fi, Fi are all the same thing.
        
        The function is wrapped with lru_cache of size 16.
        \"\"\"
        if language is None:
            if default is None:
                raise ValueError('Invalid Language Tag: None')
            else:
                language = default
        if default is None:
            return _get_language(language)
        else:
            try:
                return _get_language(language)
            except ValueError as e:
                try:
                    return _get_language(default)
                except ValueError as ex:
                    raise ex from e
    
    
    __all__ = [
        'get_language',
        'Language'
    ]
    
    """
)

with open('../src/languager/languages.py', 'w') as out:
    source = re.sub(r'^(\s+.+?):\s{2,}(.*?)\s{2,}=', r'\1: \2 =', source, flags=re.MULTILINE)
    out.write(source.format(names=names, dep=dep, lts=lts, stl=stl, mtp=mtp, ptm=ptm).strip())
    out.write('\n')
