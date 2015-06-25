all: build instal

build:
	python setup.py build

install:
	python setup.py install

clean:
	rm -rfv build/ dist/ redisjobqueue.egg-info/


