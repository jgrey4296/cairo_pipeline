#Default arg to build:
#eg: make draw=lines
ifndef ${draw}
	draw := "circles"
endif


all :
	python ./main.py ${draw}

clean :
	rm imgs/*.png

