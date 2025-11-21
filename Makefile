init:
	\
	python3 -m venv discordbotcourse; \
	source discordbotcourse/bin/activate; \
    pip install --upgrade pip; \
    pip install -r requirements.txt; \

# build_local:
# 	echo "Building Local Library"
# 	pip3 install -e .
# build:
# 	echo "Building Distribution Of Library"
# 	python3 setup.py bdist_wheel
# destroy:
# 	echo "Uninstalling Local Build Of Library"
# 	pip3 uninstall hypixel-api-lib
