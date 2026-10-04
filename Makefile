# HERMES monorepo convenience targets (paper only).
PYTHON ?= python3

.PHONY: e2e e2e-full test-ftn test-trading test-desk

e2e:            ## FTN brief → handoff contract → MINT scan → ftn_context → desk acceptance
	PYTHON=$(PYTHON) scripts/e2e_fixtures.sh

e2e-full:       ## same, plus ftn/ and trading/ pytest
	E2E_TESTS=1 PYTHON=$(PYTHON) scripts/e2e_fixtures.sh

test-ftn:
	cd ftn && $(PYTHON) -m pytest -q -p no:cacheprovider

test-trading:
	cd trading && $(PYTHON) -m pytest -q -p no:cacheprovider

test-desk:
	node desk/tests/dayContext.test.mjs
