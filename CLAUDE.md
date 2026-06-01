# Zscaler ZPA Cloud Ansible Collection Guidance

## Scope
- This repository is the `zscaler.zpacloud` collection; prioritize ZPA resources and SDK clients.
- Use the Python SDK from `/Users/wguilherme/go/src/github.com/zscaler/zscaler-sdk-python` as the source of truth for supported endpoints and request fields.
- Keep module names consistent with current collection conventions: `zpa_<resource>.py` and `zpa_<resource>_info.py`.

## Module Implementation Standards
- Use `ZPAClientHelper.zpa_argument_spec()` in every module.
- Support idempotency and `check_mode` for CRUD resources.
- For info modules, expose `id`/`name` selectors with `mutually_exclusive=[["id", "name"]]` where applicable.
- Use `collect_all_items()` for paginated list endpoints and `to_native()` for error messages.
- Normalize desired/current state before comparisons to avoid false drift.
- Avoid breaking existing auth patterns; respect legacy and OneAPI handling in `plugins/module_utils/zpa_client.py`.

## Testing and Quality Gates (Mandatory)
- Every new or enhanced module must include unit tests in `tests/unit/plugins/modules/`.
- Update existing tests whenever API behavior changes.
- Required local validation path before merge:
  - `make check-format`
  - `make new-sanity`
  - `make test:unit`
- Prefer focused tests that validate create/update/delete/idempotency/check-mode/error handling.

## CI / Sanity Requirements (Mandatory)
- `meta/runtime.yml` must declare `requires_ansible: ">=2.16.0"` (RedHat AAP minimum). Keep the CI matrix aligned: test `ansible-core` 2.16+ and verify the minimum version (2.16) against **Python 3.12**.
- For **every** Ansible version in the CI matrix there must be a matching `tests/sanity/ignore-2.XX.txt`. Adding a new matrix row (e.g. `2.20`) without the corresponding ignore file makes `validate-modules` fail every module with `missing-gplv3-license`.
- In the sanity/release workflows, install the matrix-pinned `ansible-core` **after** `poetry install`, using `poetry run pip install --force-reinstall --no-deps "<stable-tarball>"`. Because `pyproject.toml` pins `ansible-core = "*"`, running `poetry install` after the pin would upgrade ansible-core to the newest release (e.g. 2.21 on Python 3.12) and break sanity.
- Run sanity the way RedHat recommends before submitting: `ansible-test sanity --docker default --python 3.12`. The `WARNING: ... virtual environments are out-of-date ...` line is benign (cached venvs rebuild); only `ERROR:`/`FATAL:` lines or a non-zero exit indicate a real failure.
- README links must be absolute GitHub URLs (Automation Hub does not resolve relative paths); the license badge must point to `https://github.com/zscaler/zpacloud-ansible/blob/master/LICENSE`.

## API Nuances
- When API-required fields can be safely inferred (for example, known default resources), resolve them automatically to minimize user friction.
- For onboarding flows requiring secondary API verification, call the corresponding SDK verification endpoint inside module execution.
- Keep microtenant handling explicit by passing `microtenant_id` query params whenever supported by the SDK endpoint.
