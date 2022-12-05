run:
	pip install sly
	python ndp_parser.py $(filter-out $@, $(MAKECMDGOALS))
	