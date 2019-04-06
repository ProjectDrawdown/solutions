all: generate

generate:
	dot -Tsvg rrs_model_diagram.dot | python postprocess.py >rrs_model_diagram.svg
	dot -Tsvg land_model_diagram.dot | python postprocess.py >land_model_diagram.svg
