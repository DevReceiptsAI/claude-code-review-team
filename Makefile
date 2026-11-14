.PHONY: setup test pilot eval hook-test score

setup:            ## create a venv and install the one pinned dependency
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

test:             ## smoke tests + demo-app tests. No model calls, no plan usage.
	python3 -m pytest -q tests
	cd demo-app && python3 -m pytest -q

pilot:            ## 1 baseline + 1 team run on your plan login. Check /usage before and after.
	eval/run_eval.sh pilot

eval:             ## 3 runs per arm
	eval/run_eval.sh full 3

hook-test:        ## 5 commit attempts per arm (rule only vs hook)
	eval/hook_test.sh 5

score:            ## score eval/results/*.json against the answer key
	python3 eval/score.py
