lint:
	mkdir -p reports
	touch reports/pylint.txt;
	chmod -R 777 reports/
	isort bank --check
	black bank --check
	pylint bank | tee reports/pylint.txt