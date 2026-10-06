import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory

spec=importlib.util.spec_from_file_location('build_card','scripts/build_card.py')
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
cases=[
    ('{"hello":"Hello {name}"}', '{"hello":"Bonjour {name}"}', True),
    ('{"hello":"Hello {name}","bye":"Bye"}', '{"hello":"Bonjour {name}"}', True),
    ('{"hello":"Hello {name}"}', '{"hello":"Bonjour"}', False),
    ('{"hello":"Hello"}', '{"other":"Bonjour"}', False),
    ('{"hello":"Hello"}', '{"hello":""}', False),
    ('{"hello":"Hello"}', '{"hello":42}', False),
    ('{"hello":"Hello"}', '{"hello":"a","hello":"b"}', False),
    ('{"hello":"Hello"}', '{broken', False),
]
for en,fr,valid in cases:
    with TemporaryDirectory() as temporary:
        folder=Path(temporary)
        (folder/'en.json').write_text(en,encoding='utf-8')
        (folder/'fr.json').write_text(fr,encoding='utf-8')
        try:
            builder.load_translations(folder)
        except ValueError:
            assert not valid
        else:
            assert valid
print('8 translation validation cases passed.')
