# Foundation provenance

FOX source, tests, schemas, and documentation were created for this independent
repository from the project initiator's authorized specification. Examples are
synthetic. No CAE files, runtime state, credentials, private traces, or third-party
source code were copied. The pre-existing local text document is excluded.

Runtime dependencies: Python standard library only. The Python distribution
version is `0.1.0.dev0`; the human concept label is `0.1.0-concept`. The
[Python packaging versioning guide](https://packaging.python.org/en/latest/discussions/versioning/)
documents development versions. Schemas use the
[JSON Schema 2020-12 validation vocabulary](https://json-schema.org/draft/2020-12/json-schema-validation).
FOX implements only the vocabulary present in its exported schemas; it is not
a general-purpose JSON Schema processor. Development tests use a separate
validator for structural parity checks.

`requirements-dev.txt` pins the tools used for this checkpoint. The accompanying
`dependency_provenance.json` records public PyPI artifact URLs, hashes, and
declared licenses from a resolver report obtained explicitly from
`https://pypi.org/simple`. The recorded native wheel is the Windows CPython 3.14
artifact used locally; other CI platforms resolve their own wheels. This is a
provenance inventory, not a vulnerability audit or cross-platform hash lock.

Most development packages declare MIT. `packaging` declares
`Apache-2.0 OR BSD-2-Clause`. Colorama's installed license text was inspected and
is BSD-3-Clause. These tools are not vendored into FOX. Python has its own PSF
license. FOX's MIT license applies to the authored FOX material.

CI uses official `actions/checkout` v4 and `actions/setup-python` v5, pinned to
commit IDs resolved through GitHub's API during foundation work. No deployment,
token sharing, external agent access, or automatic release publishing is enabled.

Publication review covers the exact staged blobs, heuristic secret and personal
data scanning, full content review, source/license provenance, and synthetic
example checks. Scanning cannot prove the absence of every possible secret.
